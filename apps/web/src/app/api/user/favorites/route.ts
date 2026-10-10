import { NextResponse } from "next/server";
import { auth } from "@/auth";
import { db } from "@/lib/db";

const getBaseUrl = () =>
  process.env.INTERNAL_API_URL ||
  process.env.NEXT_PUBLIC_API_URL ||
  "http://127.0.0.1:8000";

async function resolveUserId(): Promise<string | null> {
  const session = await auth();
  if (!session?.user) return null;

  if (session.user.id) {
    return session.user.id;
  }

  if (session.user.email) {
    const user = await db.user.findUnique({
      where: { email: session.user.email.toLowerCase().trim() },
      select: { id: true },
    });
    return user ? user.id : null;
  }

  return null;
}

export async function GET() {
  try {
    const userId = await resolveUserId();
    if (!userId) {
      return NextResponse.json({ error: "Nicht authentifiziert" }, { status: 401 });
    }

    const baseUrl = getBaseUrl();
    const res = await fetch(`${baseUrl}/api/v1/auth/users/${userId}/favorites`, {
      cache: "no-store",
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({}));
      return NextResponse.json(
        { error: err.detail || `Fehler beim Laden der Favoriten (${res.status})` },
        { status: res.status }
      );
    }

    const data = await res.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("GET /api/user/favorites error:", error);
    return NextResponse.json(
      { error: "Verbindung zum Backend-Server fehlgeschlagen." },
      { status: 502 }
    );
  }
}
