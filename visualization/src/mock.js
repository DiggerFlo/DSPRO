export const MOCK = {
  ukraine: {
    answer: `Die NZZ berichtete 2023 und 2024 intensiv über den Krieg in der Ukraine und seine geopolitischen Folgen. Zu Jahresbeginn 2023 analysierte die Zeitung die strategische Lage und die westliche Unterstützungspolitik [1]. Die Debatte über Waffenlieferungen – insbesondere Kampfpanzer – wurde in mehreren Leitartikeln kontrovers beleuchtet [2]. Auch die humanitären Folgen und wirtschaftlichen Auswirkungen auf Europa fanden breiten Raum [3].`,
    sources: [
      { id: 1, title: "Ein Jahr Krieg: Die Ukraine zwischen Ausdauer und Erschöpfung", date: "22. Februar 2023", snippet: "Zwölf Monate nach dem russischen Einmarsch zieht die NZZ Bilanz: Die Ukraine hält stand, doch der Preis ist enorm. Militärische Analysen zeigen eine festgefahrene Frontlage.", score: 95 },
      { id: 2, title: "Leopard-Panzer für Kiew: Europa ringt um eine Entscheidung", date: "19. Januar 2023", snippet: "Die Debatte über die Lieferung westlicher Kampfpanzer spaltet Europa. Deutschland zögert, Polen und die Baltenstaaten drängen – die NZZ analysiert die Bündnispolitik.", score: 91 },
      { id: 3, title: "Energiekrise und Kriegswinter: Europa unter Druck", date: "3. Januar 2023", snippet: "Hohe Gaspreise und drohende Versorgungsengpässe prägen den Winter 2023. Die NZZ dokumentiert, wie Europa mit den wirtschaftlichen Kriegsfolgen umgeht.", score: 88 },
    ],
    followUps: ["Wie reagierte die Schweiz auf den Krieg in der Ukraine?", "Welche wirtschaftlichen Folgen hatte der Krieg für Europa?", "Wie hat die NATO auf die russische Invasion reagiert?"],
  },
  cs: {
    answer: `Der Zusammenbruch der Credit Suisse im März 2023 war für die NZZ eines der beherrschenden Themen des Jahres. Die Zeitung verfolgte den dramatischen Vertrauensverlust der Bank in einer Reihe von Analysen [1]. Die Notfusion mit der UBS, orchestriert von Bundesrat und SNB an einem einzigen Wochenende, wurde als historische Zäsur bezeichnet [2]. Fragen zur Regulierung systemrelevanter Banken wurden danach intensiv diskutiert [3].`,
    sources: [
      { id: 1, title: "Credit Suisse: Der lange Weg in die Krise", date: "15. März 2023", snippet: "Skandale, Managementwechsel und Milliardenverluste haben das Vertrauen in die Credit Suisse zerstört. Die NZZ zeichnet nach, wie eine der ältesten Schweizer Banken in die Notlage geriet.", score: 97 },
      { id: 2, title: "Das Notfall-Wochenende: UBS übernimmt Credit Suisse", date: "20. März 2023", snippet: "In einer beispiellosen Aktion erzwingt der Bundesrat die Fusion. 3 Milliarden Franken und staatliche Garantien – ein Wochenende, das die Schweizer Bankgeschichte verändert.", score: 94 },
      { id: 3, title: "Too big to fail – gescheitert?", date: "28. März 2023", snippet: "Die CS-Rettung offenbart die Grenzen der Too-big-to-fail-Regulierung. Ökonomen und Politiker streiten über das Versagen der Gesetzgebung von 2012.", score: 90 },
    ],
    followUps: ["Welche Konsequenzen hatte die CS-Übernahme für die UBS?", "Wie hat die Finma auf die Krise reagiert?", "Was bedeutet die Fusion für den Schweizer Finanzplatz?"],
  },
  ki: {
    answer: `Die Debatte um Künstliche Intelligenz und ChatGPT dominierte die NZZ-Berichterstattung 2023 wie kaum ein anderes Technologiethema. Nach dem viralen Durchbruch von ChatGPT analysierte die Zeitung die Implikationen für Bildung, Journalismus und Wirtschaft [1]. Die Risiken unkontrollierter KI-Entwicklung wurden in mehreren Kommentaren thematisiert [2]. Auch die europäische KI-Regulierung wurde intensiv verfolgt [3].`,
    sources: [
      { id: 1, title: "ChatGPT verändert die Welt – aber wie?", date: "10. Februar 2023", snippet: "Der Chatbot von OpenAI hat 100 Millionen Nutzer in zwei Monaten gewonnen. Was bedeutet das für Schulen, Universitäten und Berufe, die auf Textarbeit angewiesen sind?", score: 96 },
      { id: 2, title: "KI-Forscher fordern Pause: Zu schnell, zu riskant", date: "30. März 2023", snippet: "Hunderte Wissenschaftler fordern einen Entwicklungsstopp. Die NZZ analysiert die Argumente – und die Interessen hinter dem offenen Brief.", score: 92 },
      { id: 3, title: "EU-KI-Gesetz: Regulierung auf dem Prüfstand", date: "14. Juni 2023", snippet: "Die EU verabschiedet den weltweit ersten KI-Rechtsrahmen. Experten streiten über Chancen und Risiken für den europäischen Technologiestandort.", score: 88 },
    ],
    followUps: ["Wie verändert KI den Journalismus bei der NZZ?", "Was sind die Risiken von generativer KI laut NZZ?", "Wie positioniert sich die Schweiz in der KI-Regulierung?"],
  },
  gaza: {
    answer: `Der Gaza-Krieg nach dem Hamas-Angriff vom 7. Oktober 2023 löste intensive Berichterstattung in der NZZ aus. Die Zeitung dokumentierte die Angriffe und die israelische Militärreaktion mit täglichen Berichten [1]. Die humanitäre Lage und internationale Reaktion wurden in zahlreichen Hintergrundartikeln beleuchtet [2]. Auch die Auswirkungen auf die Schweizer Neutralitätspolitik fanden Beachtung [3].`,
    sources: [
      { id: 1, title: "Hamas-Angriff auf Israel: Der schwarze Samstag", date: "8. Oktober 2023", snippet: "In einem koordinierten Überraschungsangriff tötet die Hamas über 1200 Menschen in Israel. Die NZZ dokumentiert das Ausmass des Angriffs und die erste israelische Reaktion.", score: 98 },
      { id: 2, title: "Gaza: Humanitäre Katastrophe im Krieg", date: "2. November 2023", snippet: "Millionen Menschen sind ohne Strom, Wasser und medizinische Versorgung. Hilfsorganisationen schlagen Alarm, während über Hilfskorridore verhandelt wird.", score: 93 },
      { id: 3, title: "Schweizer Neutralität im Nahen Osten", date: "20. Oktober 2023", snippet: "Der Gaza-Krieg stellt die Schweiz vor eine aussenpolitische Zerreissprobe. Wie positioniert sich ein neutrales Land, wenn Verbündete klare Stellungnahmen fordern?", score: 87 },
    ],
    followUps: ["Wie hat die internationale Gemeinschaft auf den Gaza-Krieg reagiert?", "Welche Rolle spielt Katar bei den Verhandlungen?", "Wie berichtete die NZZ über die humanitäre Lage in Gaza?"],
  },
};

export function getResponse(q) {
  const s = q.toLowerCase();
  if (s.includes("credit suisse") || s.includes(" cs ") || s.includes("ubs")) return MOCK.cs;
  if (s.includes("ki") || s.includes("künstliche") || s.includes("chatgpt") || s.includes(" ai ") || s.includes("artificial")) return MOCK.ki;
  if (s.includes("gaza") || s.includes("nahost") || s.includes("hamas") || s.includes("israel") || s.includes("middle east")) return MOCK.gaza;
  return MOCK.ukraine;
}
