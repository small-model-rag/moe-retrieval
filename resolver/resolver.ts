import llama3Tokenizer from 'llama3-tokenizer-js'
import {getRequiredEnvVar} from "./env.js";


const sambaApiKey = getRequiredEnvVar("SAMBA_API_KEY")
const sambaClientId = getRequiredEnvVar("SAMBA_CLIENT_ID")

type UUID = string & { __brand: "uuid" }

export function randomUUID<T extends UUID = UUID>(): T {
    return "xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx".replace(/[xy]/g, c => {
        const r = Math.random() * 16 | 0
        const v = c === "x" ? r : (r & 0x3 | 0x8)
        return v.toString(16)
    }) as T
}

interface ChatMessage {
    role: "system" | "user";
    content: string;
}

interface RequestPayload {
    inputs: ChatMessage[];
    max_tokens: number;
    stop: string[];
    model: string;
}


async function makeChatCompletionRequest(
    messages: ChatMessage[],
    maxTokens: number,
    stop: string[],
    model: string
) {
    const url = `https://${sambaClientId}.snova.ai/api/v1/chat/completion`;

    const payload: RequestPayload = {
        inputs: messages,
        max_tokens: maxTokens,
        stop: stop,
        model: model,
    };

    const response = await fetch(url, {
        method: 'POST',
        headers: {
            'Authorization': `Basic ${sambaApiKey}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
    }

    // return response.json();
    const events = await response.text();

    console.log("Response: ", events);

    // take the last 2 lines: event: ..., data: {...}
    const lines = events.split('\n');

    const eventType = lines[lines.length - 4].substring(7)
    const data = JSON.parse(lines[lines.length - 3].substring(6));
    console.log("Event Type: ", eventType);

    if (!data.is_last_response) {
        throw new Error("Expected last response to be true");
    }

    return data.completion
}

async function callLlama3(messages: ChatMessage[], maxTokens: number = 800) {
    return await makeChatCompletionRequest(messages, maxTokens, ['<|eot_id|>'], 'llama3-8b')
}

interface BaseSnippet {
    id: UUID,
    filename: string;
    lastModified: string;
}

interface Image extends BaseSnippet {
    resolution: {
        width: number;
        height: number;
    }
}

interface Document extends BaseSnippet {
    content: string;
}

type Snippet = Image | Document;

function countTokens(prompt: string) {
    return llama3Tokenizer.encode(prompt).length;
}

function countMessageTokens(m: ChatMessage) {
    return countTokens(m.content);
}

export async function select(
    query: string,
    snippets: Snippet[],
    maxResults: number = 10
): Promise<UUID[]> {
    const value = {query, maxResults};

    const messages: ChatMessage[] = [
        {
            role: 'system',
            content: `You are an assistant that picks the N most relevant snippets, to help another assistant answer a user query. 
The responses will be in the form SnippetId[] - where the length is at most N.
The snippets should be ordered by relevance, and if there are no relevant snippets to the query, we can return an empty array, for optimization purposes.

Current DateTime: ${new Date().toISOString()}

---
Example:   
User:
{ query: "How much did SambaNova's revenue jump between 2017 and 2018?", maxResults: 4 }

Snippets: [
    {
        id: "j09jwfe904fsdmjf",
        content: "Title: Employment Contract Template, Body: This employment contract (this “Agreement”) is entered into as of the 1st day of January, 2022, ...",
        filename: "employment_contract_template.docx",
        lastModified: "2022-01-01T00:00:00Z"
    },
    {
        id: "w09efj2390fj3290",
        content: "Title: SambaNova Systems, Inc. - Revenue, Financials, Employees - 2017. Body: ...",
        filename: "sambanova_revenue_2017.pdf",
        lastModified: "2017-12-31T23:59:59Z"
    },
    {
        id: "jf09fj09fj34fj90",
        content: "Title: Google revenue for the quarter ending September 30, 2021 was $65.120B, a 41.6% increase year-over-year, ...",
        filename: "google_revenue_2021_q3.pdf",
        lastModified: "2021-09-30T23:59:59Z"
    },
    {
        id: "nf4fn93nf398fn43",
        content: "Title: SambaNova Revenue Report - 2018. Body: ...",
        filename: "sambanova_2018_revenue_report.pdf",
        lastModified: "2018-12-31T23:59:59Z"
    },
    {
        id: "nf4fn93nf398fn43",
        filename: "tobi_akinyemi_passport.png",
        resolution: {
            width: 500,
            height: 500
        },
        lastModified: "2018-12-31T23:59:59Z"
    },
    {
        id: "39j92jr92m09jrm0",
        content: "Title: Passport Application Form, Body: The Passport Application Form is the first requirement for any kind of British passport application. The form is ...",
        filename: "LATEST_passport_form.pdf",
        lastModified: "2022-01-01T00:00:00Z"
    },
    ...
]

Response: ["w09efj2390fj3290", "nf4fn93nf398fn43"]
---
User:
{ query: "What's the capital of France?", maxResults: 10 }

Response: [] -- No relevant snippets found.`
        },
        {
            role: 'user',
            content: JSON.stringify(value)
        }
    ];

    let totalTokens = messages.map(countMessageTokens)
        .reduce((a, b) => a + b, 0);

    const MAX_TOKEN_LIMIT = 7800;

    const finalSnippets: Snippet[] = [];

    while (totalTokens > MAX_TOKEN_LIMIT && snippets.length > 0) {
        const nextSnippet = snippets.pop()!;

        finalSnippets.push(nextSnippet);
        totalTokens += countTokens(JSON.stringify(nextSnippet))
    }

    messages.push({
        role: 'system',
        content: `Snippets: ${JSON.stringify(finalSnippets)}`
    })

    const rawResponse = await callLlama3(messages);
    const localSelection: UUID[] = JSON.parse(rawResponse);

    if (snippets.length > 0) {
        const otherSelection = await select(query, [...snippets], maxResults);
        const finalSelection: UUID[] = [...localSelection, ...otherSelection];

        if (localSelection.length === 0 || otherSelection.length === 0) {
            return finalSelection;
        }

        return select(
            query,
            finalSelection.map(id => snippets.find(s => s.id === id)!),
            maxResults
        )
    }

    return localSelection;
}