import MatchDetail from "./match-detail";

export default async function MatchPage({ params }: { params: Promise<{ match_id: string }> }) {
  const { match_id } = await params;
  return <MatchDetail key={match_id} matchId={Number(match_id)} />;
}
