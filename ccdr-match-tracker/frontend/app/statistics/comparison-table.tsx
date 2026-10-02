import { STAT_LABELS, type Comparison } from "@/lib/statistics";

export default function ComparisonTable({ data, us, opponent }: { data: Comparison; us: string; opponent: string }) {
  return <table className="comparison-table w-full table-fixed border-collapse text-sm">
    <caption className="mb-3 text-left text-lg font-semibold">Comparação de eventos</caption>
    <thead><tr className="border-b border-border">
      <th scope="col" className="w-[42%] py-3 text-left">Estatística</th>
      <th scope="col" className="break-words px-1 py-3 text-center text-secondary">{us}</th>
      <th scope="col" className="break-words px-1 py-3 text-center">{opponent}</th>
    </tr></thead>
    <tbody>{(Object.keys(STAT_LABELS) as (keyof typeof STAT_LABELS)[]).map((key) => <tr key={key} className="border-b border-border">
      <th scope="row" className="py-3 pr-2 text-left font-normal text-muted">{STAT_LABELS[key]}</th>
      <td className="px-1 py-3 text-center font-semibold tabular-nums">{data.us[key]}</td>
      <td className="px-1 py-3 text-center font-semibold tabular-nums">{data.opponent[key]}</td>
    </tr>)}</tbody>
  </table>;
}
