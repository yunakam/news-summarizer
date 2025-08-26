import { NextResponse } from "next/server";

export async function POST(req: Request) {
  const body = await req.json();
  const { url } = body;

  try {
    const res = await fetch("http://localhost:8000/summarizer/extract_article/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url }),
    });

    if (!res.ok) {
      const text = await res.text();
      return NextResponse.json({ error: text }, { status: res.status });
    }

    const data = await res.json();
    return NextResponse.json({ article: data.article });
  } catch (err) {
    return NextResponse.json({ error: String(err) }, { status: 500 });
  }
}
