import NextAuth from "next-auth";
import Google from "next-auth/providers/google";
import Credentials from "next-auth/providers/credentials";
import bcrypt from "bcrypt";
import { db } from "@/lib/db";

const backendUrl = process.env.INTERNAL_API_URL || process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export const { handlers, signIn, signOut, auth } = NextAuth({
  providers: [
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    Credentials({
      name: "E-Mail & Passwort",
      credentials: {
        email: { label: "E-Mail", type: "email" },
        password: { label: "Passwort", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Bitte gib E-Mail-Adresse und Passwort ein.");
        }

        const email = (credentials.email as string).toLowerCase().trim();
        const password = credentials.password as string;

        const user = await db.user.findUnique({
          where: { email },
        });

        if (!user || !user.hashedPassword) {
          throw new Error("E-Mail-Adresse oder Passwort ist nicht korrekt.");
        }

        if (!user.isActive) {
          throw new Error("Dein Account ist noch nicht aktiviert. Bitte bestätige zuerst deine E-Mail-Adresse über den Link in deiner Bestätigungsmail.");
        }

        const isValid = await bcrypt.compare(password, user.hashedPassword);
        if (!isValid) {
          throw new Error("E-Mail-Adresse oder Passwort ist nicht korrekt.");
        }

        return {
          id: user.id,
          email: user.email,
          name: user.name,
          role: user.role,
          image: user.avatarUrl,
        };
      },
    }),
  ],
  secret: process.env.AUTH_SECRET || "e97c11f7cbb1a8e1df388e2c3427be51543b5e408892bb66ea9d46fbe87b003a",
  trustHost: true,
  callbacks: {
    async signIn({ user, account }) {
      if (account?.provider === "google" && user.email) {
        try {
          // Synchronize user profile with backend PostgreSQL database
          const res = await fetch(`${backendUrl}/api/v1/auth/oauth-sync`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              provider: "google",
              provider_account_id: account.providerAccountId || user.id,
              email: user.email,
              name: user.name || null,
              avatar_url: user.image || null,
            }),
          });
          if (res.ok) {
            const dbUser = await res.json();
            user.id = dbUser.id;
            (user as { role?: string }).role = dbUser.role;
          }
        } catch (error) {
          console.error("Failed to sync user with backend database:", error);
        }
      }
      return true;
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.role = (user as { role?: string }).role || "user";
      }
      return token;
    },
    async session({ session, token }) {
      if (session?.user) {
        if (token?.id) {
          session.user.id = token.id as string;
        }
        (session.user as { role?: string }).role = (token?.role as string) || "user";
      }
      return session;
    },
  },
});
