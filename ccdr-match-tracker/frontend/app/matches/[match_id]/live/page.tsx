import LiveMatch from "./live-match";

export default async function LivePage({ params }: { params: Promise<{ match_id: string }> }) {
  const { match_id } = await params;
  return <LiveMatch key={match_id} matchId={Number(match_id)} />;
}
