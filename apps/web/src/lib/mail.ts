import { BrevoClient } from "@getbrevo/brevo";

interface SendVerificationEmailParams {
  toEmail: string;
  name: string;
  token: string;
}

export async function sendVerificationEmail({
  toEmail,
  name,
  token,
}: SendVerificationEmailParams) {
  const apiKey = process.env.BREVO_API_KEY;
  if (!apiKey) {
    throw new Error("BREVO_API_KEY ist nicht in den Umgebungsvariablen konfiguriert.");
  }

  const baseUrl = process.env.NEXT_PUBLIC_APP_URL || "https://politiklar.de";
  const verificationLink = `${baseUrl}/auth/verify?token=${encodeURIComponent(token)}`;

  // In Entwicklung immer auch in der Konsole ausgeben, damit man sofort testen kann
  console.log(`\n======================================================`);
  console.log(`[POLITIKLAR DOI-VERIFIZIERUNG]`);
  console.log(`Empfänger: ${toEmail} (${name})`);
  console.log(`Link: ${verificationLink}`);
  console.log(`======================================================\n`);

  const brevo = new BrevoClient({ apiKey });

  return await brevo.transactionalEmails.sendTransacEmail({
    subject: "Bestätige deine E-Mail-Adresse für Politiklar",
    sender: {
      name: "Politiklar",
      email: "noreply@politiklar.de",
    },
    to: [{ email: toEmail, name }],
    htmlContent: generateVerificationEmailHtml({
      name,
      verificationLink,
    }),
  });
}



function generateVerificationEmailHtml({
  name,
  verificationLink,
}: {
  name: string;
  verificationLink: string;
}): string {
  return `
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>E-Mail-Adresse bestätigen – Politiklar</title>
  <style>
    body {
      margin: 0;
      padding: 0;
      background-color: #0b1120;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
      color: #e2e8f0;
      -webkit-font-smoothing: antialiased;
    }
    .wrapper {
      width: 100%;
      background-color: #0b1120;
      padding: 40px 16px;
      box-sizing: border-box;
    }
    .card {
      max-width: 560px;
      margin: 0 auto;
      background-color: #1e293b;
      border: 1px solid #334155;
      border-radius: 16px;
      padding: 36px 32px;
      box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
    }
    .brand-logo {
      font-size: 22px;
      font-weight: 800;
      letter-spacing: -0.025em;
      color: #38bdf8;
      margin-bottom: 24px;
      text-transform: uppercase;
    }
    h1 {
      font-size: 20px;
      font-weight: 700;
      color: #f8fafc;
      margin-top: 0;
      margin-bottom: 16px;
    }
    p {
      font-size: 15px;
      line-height: 1.6;
      color: #94a3b8;
      margin: 0 0 20px 0;
    }
    .button-container {
      margin: 32px 0;
      text-align: center;
    }
    .btn {
      display: inline-block;
      background: #0284c7;
      background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
      color: #ffffff !important;
      text-decoration: none;
      font-weight: 600;
      font-size: 16px;
      padding: 14px 32px;
      border-radius: 8px;
      box-shadow: 0 4px 14px 0 rgba(2, 132, 199, 0.4);
    }
    .alt-link {
      font-size: 13px;
      color: #64748b;
      word-break: break-all;
    }
    .alt-link a {
      color: #38bdf8;
      text-decoration: underline;
    }
    .footer {
      border-top: 1px solid #334155;
      margin-top: 32px;
      padding-top: 20px;
      font-size: 12px;
      color: #64748b;
      text-align: center;
      line-height: 1.5;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="card">
      <div class="brand-logo">POLITIKLAR</div>
      <h1>Willkommen bei Politiklar!</h1>
      <p>Hallo <strong>${escapeHtml(name)}</strong>,</p>
      <p>
        vielen Dank für deine Registrierung. Um deinen Account zu aktivieren und sicherzustellen, 
        dass diese E-Mail-Adresse dir gehört, klicke bitte auf den folgenden Button:
      </p>
      
      <div class="button-container">
        <a href="${verificationLink}" class="btn" target="_blank" rel="noopener noreferrer">
          E-Mail bestätigen
        </a>
      </div>

      <p class="alt-link">
        Falls der Button nicht funktioniert, kopiere bitte diesen Link in deinen Browser:<br>
        <a href="${verificationLink}">${verificationLink}</a>
      </p>

      <p style="font-size: 13px; color: #64748b; margin-top: 24px;">
        <em>Dieser Link ist 24 Stunden lang gültig. Falls du dich nicht bei Politiklar registriert hast, kannst du diese Benachrichtigung einfach ignorieren.</em>
      </p>

      <div class="footer">
        &copy; ${new Date().getFullYear()} Politiklar – Transparente politische Informationen.<br>
        Dies ist eine automatische Benachrichtigung von noreply@politiklar.de.
      </div>
    </div>
  </div>
</body>
</html>
  `.trim();
}

function escapeHtml(str: string): string {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}
