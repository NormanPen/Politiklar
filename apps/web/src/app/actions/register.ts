"use server";

import crypto from "crypto";
import bcrypt from "bcrypt";
import { db } from "@/lib/db";
import { sendVerificationEmail } from "@/lib/mail";

export interface RegisterResult {
  success: boolean;
  message?: string;
  error?: string;
}

export async function registerUser(
  prevState: RegisterResult | null,
  formData: FormData
): Promise<RegisterResult> {
  const emailRaw = formData.get("email")?.toString().trim();
  const passwordRaw = formData.get("password")?.toString();
  const nameRaw = formData.get("name")?.toString().trim();

  // 1. Validierung der Basiseingaben
  if (!emailRaw || !emailRaw.includes("@")) {
    return {
      success: false,
      error: "Bitte gib eine gültige E-Mail-Adresse an.",
    };
  }

  if (!passwordRaw || passwordRaw.length < 8) {
    return {
      success: false,
      error: "Das Passwort muss mindestens 8 Zeichen lang sein.",
    };
  }

  const email = emailRaw.toLowerCase();

  // 2. Namens-Fallback: Falls kein Name angegeben, Prefix vor dem @ nutzen
  const displayName =
    nameRaw && nameRaw.length > 0 ? nameRaw : email.split("@")[0];

  try {
    // 3. Prüfen, ob bereits ein Nutzer mit dieser E-Mail existiert
    const existingUser = await db.user.findUnique({
      where: { email },
    });

    if (existingUser) {
      if (existingUser.isActive) {
        return {
          success: false,
          error: "Diese E-Mail-Adresse ist bereits registriert und aktiv. Bitte melde dich an.",
        };
      } else {
        // Bestehender inaktiver Nutzer: Token erneuern und Bestätigungsmail erneut zusenden
        const hashedPassword = await bcrypt.hash(passwordRaw, 12);
        const token = crypto.randomBytes(32).toString("hex");
        const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24h

        await db.$transaction([
          db.user.update({
            where: { id: existingUser.id },
            data: {
              hashedPassword,
              name: displayName,
            },
          }),
          db.verificationToken.deleteMany({
            where: { userId: existingUser.id },
          }),
          db.verificationToken.create({
            data: {
              token,
              userId: existingUser.id,
              expiresAt,
            },
          }),
        ]);

        await sendVerificationEmail({
          toEmail: email,
          name: displayName,
          token,
        });

        return {
          success: true,
          message:
            "Dein Account existierte bereits im unbestätigten Zustand. Wir haben dir einen neuen Bestätigungslink gesendet.",
        };
      }
    }

    // 4. Passwort sicher hashen (12 Salt-Rounds)
    const hashedPassword = await bcrypt.hash(passwordRaw, 12);

    // 5. Kryptographisch sicheren Token generieren (64 Hex-Zeichen)
    const token = crypto.randomBytes(32).toString("hex");
    const expiresAt = new Date(Date.now() + 24 * 60 * 60 * 1000); // 24h Gültigkeit

    // 6. User & Token transaktional anlegen
    const newUser = await db.user.create({
      data: {
        email,
        hashedPassword,
        name: displayName,
        isActive: false, // Double-Opt-In: Account startet inaktiv
      },
    });

    await db.verificationToken.create({
      data: {
        token,
        userId: newUser.id,
        expiresAt,
      },
    });


    // 7. E-Mail über Brevo versenden
    await sendVerificationEmail({
      toEmail: email,
      name: displayName,
      token,
    });

    return {
      success: true,
      message:
        "Registrierung erfolgreich! Wir haben dir eine Bestätigungs-E-Mail gesendet. Bitte überprüfe dein Postfach.",
    };
  } catch (error: unknown) {
    console.error("[REGISTER_ACTION_ERROR]:", error);

    const err = error as { body?: { message?: string }; message?: string; statusCode?: number };
    const message = err?.body?.message || err?.message || "";

    if (message.includes("unrecognised IP address") || err?.statusCode === 401) {
      return {
        success: false,
        error: "Brevo-Sicherheitshinweis: Die IP-Adresse muss in deinem Brevo-Konto unter https://app.brevo.com/security/authorised_ips autorisiert werden.",
      };
    }

    return {
      success: false,
      error: "Es ist ein interner Fehler aufgetreten. Bitte versuche es später noch einmal.",
    };
  }

}
