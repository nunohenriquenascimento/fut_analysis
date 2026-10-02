import type { MetadataRoute } from "next";
import { THEME_BACKGROUND } from "@/lib/brand";

export default function manifest(): MetadataRoute.Manifest {
  return {
    name: "CCDR Vila Cortez do Mondego — Sub-19",
    short_name: "CCDR Sub-19",
    lang: "pt-PT",
    start_url: "/",
    display: "standalone",
    background_color: THEME_BACKGROUND,
    theme_color: THEME_BACKGROUND,
  };
}
