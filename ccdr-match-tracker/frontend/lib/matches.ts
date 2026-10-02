import { ApiError, type MatchStatus } from "./api";

export const MATCH_STATUS: Record<MatchStatus, string> = {
  SCHEDULED: "Agendado", FIRST_HALF: "1.ª parte", HALF_TIME: "Intervalo",
  SECOND_HALF: "2.ª parte", FINISHED: "Terminado", CANCELLED: "Cancelado",
};

export function matchError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 422) return "Verifique os dados: jornada positiva, adversário, data e hora válidos.";
    if (error.status === 503) return "A base de dados está indisponível. Tente novamente.";
    return error.message;
  }
  return "Não foi possível contactar o servidor. Verifique a ligação e tente novamente.";
}

// Inputs and display both use the device's timezone; the API receives an offset in UTC.
export function matchDate(value: string): string {
  return new Date(value).toLocaleString("pt-PT", { dateStyle: "short", timeStyle: "short" });
}

export function localDateFields(value?: string): { date: string; time: string } {
  if (!value) return { date: "", time: "" };
  const local = new Date(value);
  const pad = (n: number) => String(n).padStart(2, "0");
  return { date: `${local.getFullYear()}-${pad(local.getMonth() + 1)}-${pad(local.getDate())}`,
    time: `${pad(local.getHours())}:${pad(local.getMinutes())}` };
}
