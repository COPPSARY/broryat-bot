import { getCollection, type CollectionEntry } from "astro:content";
import { DEFAULT_LOCALE, localizePath, type Locale } from "../data/site";

export type ContentCollection = "articles" | "tutorials";

type EntryMap = {
  articles: CollectionEntry<"articles">;
  tutorials: CollectionEntry<"tutorials">;
};

const tutorialOrder = [
  "forward-suspicious-message",
  "add-bot-to-group",
] as const;

export async function getLocalizedCollection<C extends ContentCollection>(
  collection: C,
  locale: Locale,
): Promise<EntryMap[C][]> {
  const entries = await getCollection(collection, ({ data }) => {
    return data.lang === locale && !data.draft;
  });

  if (collection === "articles") {
    return entries.sort((a, b) => {
      return b.data.date.getTime() - a.data.date.getTime();
    }) as EntryMap[C][];
  }

  return entries.sort((a, b) => {
    return (
      tutorialOrder.indexOf(a.data.translationId as (typeof tutorialOrder)[number]) -
      tutorialOrder.indexOf(b.data.translationId as (typeof tutorialOrder)[number])
    );
  }) as EntryMap[C][];
}

export async function getTranslatedEntry<C extends ContentCollection>(
  collection: C,
  translationId: string,
  locale: Locale,
): Promise<EntryMap[C] | undefined> {
  const entries = await getLocalizedCollection(collection, locale);
  return entries.find((entry) => entry.data.translationId === translationId);
}

export function getEntryUrl(
  collection: ContentCollection,
  locale: Locale,
  translationId: string,
) {
  return localizePath(locale, `${collection}/${translationId}`);
}

export function getAlternateLocale(locale: Locale): Locale {
  return locale === DEFAULT_LOCALE ? "en" : DEFAULT_LOCALE;
}
