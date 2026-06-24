import { DashboardClient } from "@/components/DashboardClient";
import { getFishponds } from "@/lib/server-data";

export default function Page() {
  return <DashboardClient ponds={getFishponds()} />;
}
