import CompetitionScreen from "@/app/competitions/competition-screen";

export default async function Page({ params }: { params: Promise<{ competition_id: string }> }) {
  const { competition_id } = await params;
  return <CompetitionScreen key={`${competition_id}-manage`} competitionId={Number(competition_id)} view="manage" />;
}
