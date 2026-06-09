import { NextResponse } from "next/server";
import fs from "fs";
import path from "path";

export async function GET() {
  try {
    const filePath = path.join(
      process.cwd(),
      "..",
      "data",
      "raw_articles.json"
    );

    const content = fs.readFileSync(
      filePath,
      "utf-8"
    );

    return NextResponse.json(
      JSON.parse(content)
    );
  } catch (err) {
    return NextResponse.json(
      { error: "Cannot load raw articles" },
      { status: 500 }
    );
  }
}