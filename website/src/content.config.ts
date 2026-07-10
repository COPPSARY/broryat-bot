import { defineCollection, z } from "astro:content";

const articles = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    date: z.coerce.date(),
    lang: z.enum(["kh", "en"]),
    translationId: z.string(),
    tag: z.string(),
    coverImage: z.string(),
    draft: z.boolean().default(false),
  }),
});

const tutorials = defineCollection({
  type: "content",
  schema: z.object({
    title: z.string(),
    description: z.string(),
    lang: z.enum(["kh", "en"]),
    translationId: z.string(),
    coverImage: z.string(),
    videoUrl: z.string().optional().nullable(),
    draft: z.boolean().default(false),
  }),
});

export const collections = { articles, tutorials };
