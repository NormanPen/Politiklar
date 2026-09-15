"use server";

import { db } from "@/lib/db";

export type VerificationStatus =
  | "success"
  | "expired"
  | "invalid"
  | "missing_token"
  | "server_error";

export interface VerifyTokenResult {
  success: boolean;
  status: VerificationStatus;
  message: string;
}

export async function verifyToken(token?: string | null): Promise<VerifyTokenResult> {
  if (!token) {
    return {
      success: false,
      status: "missing_token",
      message: "Kein Bestätigungstoken übergeben.",
    };
  }

  try {
    // 1. Token in der Datenbank suchen
    const record = await db.verificationToken.findUnique({
      where: { token },
      include: { user: true },
    });

    // 2. Token-Existenz prüfen
    if (!record) {
      return {
        success: false,
        status: "invalid",
        message: "Der Bestätigungslink ist ungültig oder wurde bereits verwendet.",
      };
    }

    // 3. Gültigkeit (24h) prüfen
    const now = new Date();
    if (record.expiresAt < now) {
      // Abgelaufenen Token aufräumen
      await db.verificationToken.delete({
        where: { id: record.id },
      });
      return {
        success: false,
        status: "expired",
        message: "Der Bestätigungslink ist abgelaufen.",
      };
    }

    // 4. Atomar: User aktivieren & Token löschen (Single-Use)
    await db.$transaction([
      db.user.update({
        where: { id: record.userId },
        data: {
          isActive: true,
          emailVerified: now,
        },
      }),
      db.verificationToken.delete({
        where: { id: record.id },
      }),
    ]);

    return {
      success: true,
      status: "success",
      message: "E-Mail-Adresse erfolgreich verifiziert.",
    };
  } catch (error) {
    console.error("[VERIFY_TOKEN_ERROR]:", error);
    return {
      success: false,
      status: "server_error",
      message: "Ein technischer Fehler ist aufgetreten.",
    };
  }
}
