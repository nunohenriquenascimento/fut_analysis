import MatchStatistics from "./match-statistics";

export default async function StatsPage({ params }: { params: Promise<{ match_id: string }> }) {
  const { match_id } = await params;
  return <MatchStatistics key={match_id} matchId={Number(match_id)} />;
}
