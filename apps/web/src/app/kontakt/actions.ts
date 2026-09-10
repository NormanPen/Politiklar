"use server";

export type ContactFormState = {
  success?: boolean;
  message?: string;
  errors?: {
    name?: string;
    email?: string;
    message?: string;
  };
};

/**
 * Server Action für das Kontaktformular.
 * Aktuell als Dummy implementiert (simulierter Versand & Server-Log).
 * Kann später direkt mit nodemailer oder einem E-Mail-Provider verbunden werden.
 */
export async function submitContactForm(
  _prevState: ContactFormState,
  formData: FormData
): Promise<ContactFormState> {
  const name = formData.get("name")?.toString().trim();
  const email = formData.get("email")?.toString().trim();
  const message = formData.get("message")?.toString().trim();

  // 1. Unsichtbarer Honeypot-Spamschutz (wird von Bots oft ausgefüllt)
  const honeypot = formData.get("website_hp")?.toString();
  if (honeypot) {
    // Fake-Erfolg zurückgeben, damit der Bot denkt, es hätte geklappt
    return {
      success: true,
      message: "Vielen Dank! Ihre Nachricht wurde erfolgreich übermittelt.",
    };
  }

  // 2. Validierung
  const errors: ContactFormState["errors"] = {};

  if (!name || name.length < 2) {
    errors.name = "Bitte geben Sie Ihren Namen ein (mindestens 2 Zeichen).";
  }

  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email || !emailRegex.test(email)) {
    errors.email = "Bitte geben Sie eine gültige E-Mail-Adresse ein.";
  }

  if (!message || message.length < 10) {
    errors.message = "Ihre Nachricht sollte mindestens 10 Zeichen lang sein.";
  }

  if (Object.keys(errors).length > 0) {
    return {
      success: false,
      errors,
    };
  }

  // 3. Simulierter Versand (Dummy)
  // Hier wird später der nodemailer-Aufruf eingefügt.
  console.log("[Kontaktformular - Dummy-Versand]:", {
    name,
    email,
    message,
    timestamp: new Date().toISOString(),
  });

  // Kurze Verzögerung für realistische UX
  await new Promise((resolve) => setTimeout(resolve, 600));

  return {
    success: true,
    message: "Vielen Dank für Ihre Nachricht! Wir werden uns baldmöglichst bei Ihnen melden.",
  };
}
