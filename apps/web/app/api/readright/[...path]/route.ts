import { NextRequest, NextResponse } from "next/server";

function backendBase() {
  const value = process.env.READRIGHT_API_BASE || process.env.NEXT_PUBLIC_READRIGHT_API_BASE;
  if (!value) throw new Error("READRIGHT_API_BASE is not configured");
  return value.replace(/\/$/, "");
}

async function proxy(request: NextRequest, context: { params: Promise<{ path: string[] }> }) {
  try {
    const { path } = await context.params;
    const url = new URL(`${backendBase()}/${path.join("/")}`);
    request.nextUrl.searchParams.forEach((value, key) => url.searchParams.append(key, value));

    const headers = new Headers();
    const contentType = request.headers.get("content-type");
    if (contentType) headers.set("content-type", contentType);

    const init: RequestInit = {
      method: request.method,
      headers,
      cache: "no-store",
    };

    if (!["GET", "HEAD"].includes(request.method)) {
      init.body = await request.text();
    }

    const response = await fetch(url, init);
    const body = await response.text();
    return new NextResponse(body, {
      status: response.status,
      headers: {
        "content-type": response.headers.get("content-type") || "application/json",
        "cache-control": "no-store",
      },
    });
  } catch (error) {
    return NextResponse.json(
      {
        detail: error instanceof Error ? error.message : "ReadRight engine unavailable",
      },
      { status: 502 },
    );
  }
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;
