export const SITE = {
  name: "Broryat",
  wordmark: "ប្រយ័ត្ន",
  telegramUrl: "https://t.me/broryat_bot",
  telegramHandle: "@broryat_bot",
  footerLinks: [
    {
      label: "Sayana Studio",
      href: "https://sayanastudio.tech/",
    },
    {
      label: "Instagram",
      href: "https://www.instagram.com/sayana.studio",
    },
  ],
} as const;

export const LOCALES = ["kh", "en"] as const;
export type Locale = (typeof LOCALES)[number];
export const DEFAULT_LOCALE: Locale = "kh";

export const SEO = {
  siteUrl: "https://broryat.tech",
  defaultOgImage: "/branding/logo.png",
  // Maps our locale codes to full BCP-47 / OG locale codes
  ogLocale: {
    kh: "km_KH",
    en: "en_US",
  },
  hreflang: {
    kh: "km",
    en: "en",
  },
  themeColor: "#032ea1",
  keywords: {
    kh: [
      "ប្រយ័ត្ន",
      "Broryat",
      "AI Bot ការពារការបោកប្រាស់",
      "ពិនិត្យ link ក្លែងក្លាយ",
      "ស្កេនឯកសារមេរោគ",
      "សុវត្ថិភាព Telegram",
      "phishing ខ្មែរ",
      "ការពារការបោកប្រាស់ online",
      "ពិនិត្យសារសង្ស័យ Telegram",
      "malware APK EXE",
      "VirusTotal Telegram bot",
      "សន្តិសុខតាមអ៊ីនធឺណិត កម្ពុជា",
    ],
    en: [
      "Broryat",
      "Telegram scam checker",
      "phishing detection bot",
      "check suspicious link Telegram",
      "malware file scanner",
      "Telegram security bot",
      "scam link checker Cambodia",
      "VirusTotal Telegram",
      "APK EXE ZIP PDF malware scan",
      "Khmer scam protection",
      "anti phishing Telegram",
      "cybersecurity Cambodia",
    ],
  },
} as const;

export const HOME_FEATURES = {
  kh: [
    {
      title: "វិភាគផ្ទៀងផ្ទាត់ខ្លឹមសារសារដោយ AI",
      description:
        "ឆ្លាតវៃក្នុងការសម្គាល់ភាសាគំរាមកំហែងបង្កភ័យ ក្លែងបន្លំជាធនាគារ បង្ខំឱ្យផ្ទេរប្រាក់ និងល្បិចបោកប្រាស់ទូទៅ ទាំងភាសាខ្មែរនិងអង់គ្លេស។",
    },
    {
      title: "ស្កេនតំណភ្ជាប់ និងឯកសារគ្រោះថ្នាក់",
      description:
        "ពិនិត្យមើល URL និងឯកសារប្រភេទ APK, EXE, ZIP, PDF ដែលជនខិលខូចនិយមប្រើដើម្បីបោកប្រាស់ ឬបង្កប់មេរោគ (Malware) លើ Telegram តាមរយៈបច្ចេកវិទ្យា VirusTotal v3 API។",
    },
    {
      title: "ប្រព័ន្ធការពារសម្រាប់ក្រុមពិភាក្សា (Group Chat)",
      description:
        "គ្រាន់តែទាញ Bot ចូលទៅក្នុងគ្រុប សមាជិកទាំងអស់នឹងមានកន្លែងសុវត្ថិភាពមួយសម្រាប់ផ្ទៀងផ្ទាត់រាល់មាតិកាសង្ស័យ មុននឹងសម្រេចចិត្តចុចបើក។",
    },
  ],
  en: [
    {
      title: "AI intent analysis",
      description:
        "Detects urgency language, bank impersonation, money-transfer pressure, and common scam tactics across Khmer and English messages.",
    },
    {
      title: "Link and file scanning",
      description:
        "Checks URLs, APKs, EXEs, ZIPs, PDFs, and the file types attackers usually use to deliver phishing or malware on Telegram, powered by the VirusTotal v3 API.",
    },
    {
      title: "Group chat protection",
      description:
        "Add the bot to a group so members have one place to review suspicious content before anyone opens it.",
    },
  ],
} as const;

export const HOME_EXAMPLES = {
  kh: [
    {
      id: "phishing",
      tabTitle: "សារល្បិចបោក (Phishing)",
      tabDescription: "តំណភ្ជាប់បោកប្រាស់ទូទៅ",
      message:
        "សារបោកប្រាស់ភាគច្រើនចូលចិត្តប្រាប់ថា អ្នកឈ្នះរង្វាន់ ត្រូវផ្ទៀងផ្ទាត់គណនី ឬជួបបញ្ហាបន្ទាន់ណាមួយ រួចបង្ខំឱ្យអ្នកចុចចូលទៅកាន់តំណភ្ជាប់ (Link) ភ្លាមៗ។",
      analysis:
        "ចំណុចសម្គាល់គឺការប្រើពាក្យសម្តីដេញដោលឱ្យប្រញាប់ និងការនាំអ្នកទៅកាន់គេហទំព័រ (Domain) ក្លែងក្លាយ។ នៅពេលចុចចូល គេនឹងទាមទារឱ្យអ្នកបំពេញលេខសម្ងាត់ (Password) លេខកូដ OTP ឬព័ត៌មានគណនីធនាគារ។",
      recommendation:
        "ដាច់ខាតកុំចុចតំណភ្ជាប់ពីសារបែបនេះ។ ត្រូវពិនិត្យឈ្មោះគេហទំព័រឱ្យបានច្បាស់លាស់ ឬបើមិនច្បាស់ចិត្តទេ គ្រាន់តែផ្ញើ Link នោះមកកាន់ Broryat ដើម្បីជួយពិនិត្យមុនសិន។",
      image: "/assets/attack-1-link.PNG",
    },
    {
      id: "malware",
      tabTitle: "ឯកសារបង្កប់មេរោគ",
      tabDescription: "ប្រភេទឯកសារគួរឱ្យសង្ស័យ",
      message:
        "ឯកសារគ្រោះថ្នាក់ច្រើនតែបន្លំខ្លួនជាប្រវត្តិរូបសង្ខេប (CV) វិក្កយបត្រ (Invoice/Receipt) ឬកំណែទម្រង់កម្មវិធី (App Update) ដោយប្រើកន្ទុយឯកសារប្លែកៗដូចជា `.pdf.z`, `.apk` ឬជាហ្វាយបង្រួម (Archive) ដែលលាក់មេរោគនៅខាងក្នុង។",
      analysis:
        "គ្រោះថ្នាក់ពិតប្រាកដមិនមែននៅលើឈ្មោះឡើយ គឺនៅលើកន្ទុយឯកសារពិតប្រាកដ និងបញ្ជាដែលវានឹងដំណើរការ។ ឯកសារទាំងនេះអាចជាកម្មវិធីបង្កប់ ឬកូដមេរោគ (Payload) ដែលលួចដំឡើង និងលួចយកទិន្នន័យផ្ទាល់ខ្លួនរបស់អ្នក។",
      recommendation:
        "សូមកុំបើកឯកសារដែលមានកន្ទុយប្លែកៗឱ្យសោះ។ ត្រូវផ្ញើមកស្កេនសិន ឬបើមានគេផ្ញើមកដោយអះអាងថាជា CV ឬឯកសារការងារ សូមប្រាប់គេឱ្យផ្ញើជាឯកសារ PDF ធម្មតាវិញ តាមរយៈប្រភពដែលទុកចិត្តបាន។",
      image: "/assets/attack-2-file.PNG",
    },
  ],
  en: [
    {
      id: "phishing",
      tabTitle: "Phishing message",
      tabDescription: "General phishing link",
      message:
        "Phishing messages often claim you won a reward, need to verify an account, or must respond to an urgent problem, then push you toward a link immediately.",
      analysis:
        "The key signs are urgency and a non-official domain. After you click, the page may ask for your password, OTP codes, banking details, or other private information.",
      recommendation:
        "Do not open links from messages like this without checking them first. Verify the domain carefully, and if you are unsure, send the link to Broryat before opening it.",
      image: "/assets/attack-1-link.PNG",
    },
    {
      id: "malware",
      tabTitle: "Malicious file",
      tabDescription: "General suspicious file",
      message:
        "Suspicious files are often disguised as resumes, invoices, receipts, or app updates, and may use unusual extensions like `.pdf.z`, `.apk`, or archives that hide another file inside.",
      analysis:
        "The real issue is not just the file name but the true extension and what the file actually runs. Files like this may be archives or payloads that hide malware installation or data theft.",
      recommendation:
        "Do not open files with suspicious extensions. Scan them first, and if someone claims the file is a resume or work document, ask for a normal PDF through a trusted channel.",
      image: "/assets/attack-2-file.PNG",
    },
  ],
} as const;

export const UI = {
  kh: {
    brandName: "ប្រយ័ត្ន",
    localeLabel: "ខ្មែរ",
    alternateLocaleLabel: "EN",
    home: "ទំព័រដើម",
    articles: "អត្ថបទ",
    tutorials: "មេរៀន",
    navHow: "របៀបប្រើប្រាស់",
    navNews: "ព័ត៌មាន",
    navGuides: "មគ្គុទ្ទេសក៍",
    navFaq: "សំណួរញឹកញាប់ (FAQ)",
    latestArticles: "អត្ថបទថ្មីៗ",
    latestArticlesIntro:
      "អត្ថបទណែនាំខ្លីៗ និងជាក់ស្តែងក្នុងការការពារខ្លួនពីល្បិចបោកប្រាស់ តំណភ្ជាប់ក្លែងក្លាយ និងឯកសារគ្រោះថ្នាក់។",
    tutorialsIntro:
      "មេរៀនខ្លីៗ ងាយយល់ សម្រាប់ការប្រើប្រាស់ Bot ដើម្បីស្កេនសារ និងការពារក្រុម Telegram របស់អ្នក។",
    tutorialsTitle: "មេរៀន",
    readArticle: "អានអត្ថបទ",
    openTutorial: "មើលមេរៀន",
    browseArticles: "មើលអត្ថបទទាំងអស់",
    browseTutorials: "មើលមេរៀនទាំងអស់",
    goToBot: "ទៅកាន់ Telegram Bot",
    heroTitle: "ប្រុងប្រយ័ត្នលើ Telegram!",
    heroBody:
      "Broryat គឺជា AI Bot ដែលជួយការពារអ្នកពីការបោកប្រាស់តាមប្រព័ន្ធអ៊ីនធឺណិត។ គ្រាន់តែផ្ញើតំណភ្ជាប់ (Link) សារ ឬឯកសារដែលអ្នកសង្ស័យមកកាន់ Bot នោះវានឹងវិភាគរកហានិភ័យ រួចផ្តល់ការណែនាំដល់អ្នកភ្លាមៗ។",
    heroHandleLabel: "គណនី Telegram ផ្លូវការ",
    heroImage: "/assets/hero-image.png",
    heroImageCredit:
      "ប្រភពរូបភាព៖ ផ្អែកលើរូបភាពផ្សព្វផ្សាយរបស់នាយកដ្ឋានប្រឆាំងបទល្មើសបច្ចេកវិទ្យា អំពីការវាយប្រហារបោកប្រាស់ (Phishing) ថ្មីៗលើ Telegram។ Kiripost តាមរយៈ ACCD",
    featuresTitle: "សមត្ថភាពរបស់ Broryat AI",
    featuresIntro:
      "Broryat ផ្តោតលើការស្វែងរកទម្រង់សារបោកប្រាស់ ដែលមនុស្សទូទៅជួបប្រទះពិតប្រាកដនៅក្នុងប្រអប់សារ និងសារដែលត្រូវបាន Forward ចែករំលែកតៗគ្នា។",
    exampleTitle: "ឧទាហរណ៍",
    exampleIntro:
      "ខាងក្រោមនេះជាទម្រង់សារបោកប្រាស់ទូទៅដែលជនខិលខូចនិយមប្រើប្រាស់៖",
    exampleMessageLabel: "ទម្រង់សារនៅលើ Telegram",
    exampleAnalysisLabel: "លទ្ធផលនៃការវិភាគ",
    exampleRecommendationLabel: "ដំបូន្មានដែលត្រូវអនុវត្ត",
    howToUseTitle: "របៀបប្រើប្រាស់",
    howToUseIntro:
      "ងាយៗត្រឹម ៣ ជំហាន មិនចាំបាច់មានការកំណត់ (Setting) ឬផ្ទាំង Dashboard ស្មុគស្មាញឡើយ។ គ្រាន់តែបើក Telegram រួចផ្ញើមាតិកាសង្ស័យទៅកាន់ Bot ជាការស្រេច។",
    howToUseSteps: [
      {
        step: "01",
        title: "ស្វែងរក Bot ផ្លូវការ",
        body:
          "បើកកម្មវិធី Telegram រួចស្វែងរកឈ្មោះ `@broryat_bot` ដើម្បីចាប់ផ្តើមជជែកជាមួយ Bot ផ្លូវការ។",
        image: "/3-simple-steps/step1.PNG",
        imageVariant: "wide",
      },
      {
        step: "02",
        title: "ផ្ញើសារ ឬឯកសារសង្ស័យ",
        body:
          "Forward សារ ចម្លងតំណភ្ជាប់ (Link) ឬផ្ញើឯកសារទៅកាន់ Bot ដោយផ្ទាល់ ដោយមិនបាច់ចុចបើកវាជាមុនឡើយ។",
        image: "/3-simple-steps/step2.PNG",
        imageVariant: "tall",
      },
      {
        step: "03",
        title: "ទទួលបានលទ្ធផលភ្លាមៗ",
        body:
          "Bot នឹងឆ្លើយតបមកវិញនូវកម្រិតហានិភ័យ រួមទាំងជំហានអនុវត្តជាក់ស្តែង ដើម្បីឱ្យអ្នកដឹងថាគួរចៀសវាង ឬត្រូវផ្ទៀងផ្ទាត់បន្ថែម។",
        image: "/3-simple-steps/step3.png",
        imageVariant: "medium",
      },
    ],
    newsTitle: "ព័ត៌មាន",
    newsIntro:
      "អត្ថបទថ្មីៗដើម្បីជួយអ្នកឱ្យទាន់ល្បិចបោកប្រាស់ថ្មីៗ និងចេះវិធីការពារគណនី Telegram ឱ្យមានសុវត្ថិភាព។",
    guidesTitle: "មគ្គុទ្ទេសក៍",
    guidesIntro:
      "ស្វែងយល់ពីរបៀបប្រើប្រាស់ Bot និងវិធីសាស្ត្រការពារខ្លួនដែលអ្នកគួរអាន មុននឹងសម្រេចចិត្តបើក ឬចែករំលែកមាតិកាសង្ស័យណាមួយ។",
    ctaTitle: "តើអ្នកកំពុងមានសារគួរឱ្យសង្ស័យមែនទេ?",
    ctaBody:
      "បើក Telegram ហើយផ្ញើវាទៅកាន់ Broryat ឥឡូវនេះ ដើម្បីទទួលបានការវិភាគរកហានិភ័យភ្លាមៗ។",
    footerNote: "រចនា និងអភិវឌ្ឍដោយ Sayana Studio",
    backToArticles: "ត្រឡប់ទៅទំព័រអត្ថបទ",
    backToTutorials: "ត្រឡប់ទៅទំព័រមេរៀន",
    articleLabel: "អត្ថបទ",
    tutorialLabel: "មេរៀន",
    videoComingSoon: "វីដេអូណែនាំនឹងមកដល់ឆាប់ៗនេះ",
    videoPlaceholder:
      "វីដេអូកំពុងរៀបចំផលិត។ សូមអានជំហានណែនាំខាងក្រោមជាបណ្តោះអាសន្ន រហូតដល់វីដេអូត្រូវបានបង្ហោះជាផ្លូវការ។",
  },
  en: {
    brandName: "Broryat",
    localeLabel: "English",
    alternateLocaleLabel: "ខ្មែរ",
    home: "Home",
    articles: "Articles",
    tutorials: "Tutorials",
    navHow: "Usage",
    navNews: "News",
    navGuides: "Guides",
    navFaq: "FAQ",
    latestArticles: "Latest Articles",
    latestArticlesIntro:
      "Practical reads on phishing, malicious files, and safer Telegram habits.",
    tutorialsIntro:
      "Short walkthroughs for using the bot in private chats and Telegram groups.",
    tutorialsTitle: "Tutorials",
    readArticle: "Read article",
    openTutorial: "Open tutorial",
    browseArticles: "Browse all articles",
    browseTutorials: "Browse all tutorials",
    goToBot: "Telegram Bot",
    heroTitle: "Becareful of Scammers on Telegram!",
    heroBody:
      "Broryat is an AI bot that helps protect people from online scams. Send the bot a suspicious link, message, or file to analyze the risk and get immediate guidance.",
    heroHandleLabel: "Telegram handle",
    heroImage: "/assets/hero-image.png",
    heroImageCredit:
      "Credit: the poster of the Anti-Cyber Crime Department has observed recent phishing attacks on Telegram. Kiripost via ACCD",
    featuresTitle: "Capabilities of Broryat AI",
    featuresIntro:
      "Broryat focuses on the message patterns people actually receive in Telegram chats and forwarded content.",
    exampleTitle: "Example messages",
    exampleIntro:
      "Below are common message patterns used by bad actors:",
    exampleMessageLabel: "Telegram Message",
    exampleAnalysisLabel: "Analysis",
    exampleRecommendationLabel: "Recommendation",
    howToUseTitle: "Usage",
    howToUseIntro:
      "3 Simple Steps, No dashboard and no extra setup. Open Telegram and send the suspicious content to the bot.",
    howToUseSteps: [
      {
        step: "01",
        title: "Find the official bot",
        body:
          "Open Telegram and search for `@broryat_bot` to start a chat with the official bot.",
        image: "/3-simple-steps/step1.PNG",
        imageVariant: "wide",
      },
      {
        step: "02",
        title: "Send the suspicious content",
        body:
          "Forward the message, paste the link, or send the file to the bot without opening it first.",
        image: "/3-simple-steps/step2.PNG",
        imageVariant: "tall",
      },
      {
        step: "03",
        title: "Get the review back fast",
        body:
          "The bot replies with a risk judgment and a practical next step so you know whether to avoid it or verify further.",
        image: "/3-simple-steps/step3.png",
        imageVariant: "medium",
      },
    ],
    newsTitle: "News",
    newsIntro:
      "Recent reads on scam patterns, fake links, and protecting your Telegram account.",
    guidesTitle: "Guides",
    guidesIntro:
      "Use these walkthroughs and how-to reads before you open or forward suspicious content.",
    ctaTitle: "Have a suspicious message?",
    ctaBody:
      "Open Telegram and send it to Broryat for an immediate risk review.",
    footerNote: "Designed and built by Sayana Studio",
    backToArticles: "Back to articles",
    backToTutorials: "Back to tutorials",
    articleLabel: "Article",
    tutorialLabel: "Tutorial",
    videoComingSoon: "Video coming soon",
    videoPlaceholder:
      "Recording is still pending. Use the written steps below until the video is published.",
  },
} as const;

export function isLocale(value: string): value is Locale {
  return LOCALES.includes(value as Locale);
}

export function formatDate(date: Date, locale: Locale) {
  return new Intl.DateTimeFormat(locale === "kh" ? "km-KH" : "en-US", {
    day: "numeric",
    month: "short",
    year: "numeric",
  }).format(date);
}

export function localizePath(locale: Locale, path = "") {
  const clean = path.replace(/^\/|\/$/g, "");

  if (!clean) {
    return locale === DEFAULT_LOCALE ? "/" : `/${locale}/`;
  }

  return locale === DEFAULT_LOCALE ? `/${clean}/` : `/${locale}/${clean}/`;
}
