import { NextRequest, NextResponse } from "next/server";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { mdbId, question } = body;

    if (!mdbId || typeof mdbId !== "number") {
      return NextResponse.json(
        { error: "Ungültige oder fehlende MdB-ID." },
        { status: 400 }
      );
    }

    if (!question || typeof question !== "string" || question.trim().length < 3) {
      return NextResponse.json(
        { error: "Die Frage muss mindestens 3 Zeichen lang sein." },
        { status: 400 }
      );
    }

    // INTERNAL_API_URL im Docker-Container http://api:8000 bzw. http://127.0.0.1:8000
    const baseUrl =
      process.env.INTERNAL_API_URL ||
      process.env.NEXT_PUBLIC_API_URL ||
      "http://127.0.0.1:8000";

    const backendRes = await fetch(`${baseUrl}/api/v1/members/${mdbId}/ask`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ question: question.trim() }),
      cache: "no-store",
    });

    if (!backendRes.ok) {
      const errorData = await backendRes.json().catch(() => ({}));
      return NextResponse.json(
        {
          error:
            errorData.detail ||
            `Fehler beim Abrufen der Antwort (HTTP ${backendRes.status}).`,
        },
        { status: backendRes.status }
      );
    }

    const data = await backendRes.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error("Politician chat route error:", error);
    return NextResponse.json(
      {
        error:
          "Verbindungsfehler zum Backend. Bitte prüfe, ob der FastAPI-Dienst aktiv ist.",
      },
      { status: 502 }
    );
  }
}
