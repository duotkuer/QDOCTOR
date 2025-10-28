// app/api/chat/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message } = body;

    if (!message) {
      return NextResponse.json({ error: 'Message is required' }, { status: 400 });
    }

    const payload = {
      question: message,                 // map frontend -> backend field
      top_k: 3     // optional param
    };

    const BACKEND = process.env.BACKEND_URL ?? 'http://127.0.0.1:8000';
    const backendResponse = await fetch(`${BACKEND}/ask`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const respText = await backendResponse.text();

    if (!backendResponse.ok) {
      // return backend validation / error details for debugging
      console.error('Backend error:', backendResponse.status, respText);
      return NextResponse.json(
        { error: 'Backend error', detail: respText },
        { status: backendResponse.status }
      );
    }

    let data;
    try { data = JSON.parse(respText); } catch { data = respText; }

    return NextResponse.json(data);
  } catch (error) {
    console.error('Error forwarding request to backend:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}