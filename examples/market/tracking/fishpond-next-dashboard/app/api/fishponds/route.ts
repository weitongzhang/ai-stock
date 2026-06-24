import { NextResponse } from "next/server";
import { getFishponds } from "@/lib/server-data";

export const dynamic = "force-dynamic";

export function GET() {
  return NextResponse.json({ ponds: getFishponds() });
}
