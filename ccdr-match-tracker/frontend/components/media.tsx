"use client";

import { useState } from "react";
import { CLUB } from "@/lib/brand";

function Asset({ src, alt, fallback, className }: { src?: string | null; alt: string; fallback: string; className: string }) {
  const [failed, setFailed] = useState<string | null>(null);
  // Only local public paths are supported in this phase, including for legacy data.
  const local = src && /^\/(?!\/)[A-Za-z0-9_./-]+$/.test(src) && !src.includes("..");
  return <span className={`asset ${className}`}>
    {local && failed !== src
      // Local assets may be supplied after the build; use the browser's native error fallback.
      // eslint-disable-next-line @next/next/no-img-element
      ? <img src={src} alt={alt} ref={(element) => { if (element?.complete && element.naturalWidth === 0) setFailed(src); }} onError={() => setFailed(src)} width={64} height={64} />
      : <span role="img" aria-label={alt}>{fallback}</span>}
  </span>;
}

export function PlayerAvatar({ name, photoPath, number, size = "md" }: { name: string; photoPath?: string | null; number?: number | null; size?: "sm" | "md" | "lg" }) {
  const initials = name.trim().split(/\s+/).map((word) => word[0]).filter(Boolean);
  const fallback = initials.length ? `${initials[0]}${initials.length > 1 ? initials.at(-1) : ""}`.toLocaleUpperCase("pt") : String(number ?? "—");
  return <Asset src={photoPath} alt={`Foto de ${name}`} fallback={fallback} className={`avatar asset-${size}`} />;
}

export function TeamCrest({ name, path, club = false, size = "md" }: { name: string; path?: string | null; club?: boolean; size?: "sm" | "md" | "lg" }) {
  return <Asset src={path ?? (club ? CLUB.crest : null)} alt={`Emblema de ${name}`} fallback="—" className={`crest asset-${size}`} />;
}
