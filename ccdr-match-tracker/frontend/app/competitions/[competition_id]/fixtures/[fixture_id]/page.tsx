import CompetitionScreen from "@/app/competitions/competition-screen";

export default async function Page({ params }: { params: Promise<{ competition_id: string; fixture_id: string }> }) {
  const { competition_id, fixture_id } = await params;
  return <CompetitionScreen key={`${competition_id}-${fixture_id}`} competitionId={Number(competition_id)} fixtureId={Number(fixture_id)} view="fixture" />;
}
