/**
 * StoryCrafter MCP Server
 * AI-powered backlog generator for VISHKAR consensus discussions
 */

import { NextRequest, NextResponse } from 'next/server';
import axios from 'axios';

// StoryCrafter service URL (deployed separately)
const STORYCRAFTER_SERVICE_URL = process.env.STORYCRAFTER_SERVICE_URL || 'https://storycrafter-service.vercel.app';

// ============================================================
// TYPES
// ============================================================

interface ConsensusMessage {
  role: string;
  content: string;
}

interface ProjectMetadata {
  project_name?: string;
  project_description?: string;
  target_users?: string;
  platform?: string;
  timeline?: string;
  team_size?: string;
}

interface MCPRequest {
  method: string;
  params?: {
    tool?: string;
    arguments?: Record<string, any>;
  };
}

// ============================================================
// MCP TOOLS
// ============================================================

const MCP_TOOLS = [
  {
    name: 'generate_backlog',
    description: 'Generate complete project backlog from VISHKAR 3-agent consensus discussion. Returns 6-8 epics with 20-40 detailed user stories, acceptance criteria, technical tasks, story points, and time estimates.',
    inputSchema: {
      type: 'object',
      properties: {
        consensus_messages: {
          type: 'array',
          description: 'List of messages from 3-agent consensus (system, alex, blake, casey)',
          items: {
            type: 'object',
            properties: {
              role: {
                type: 'string',
                enum: ['system', 'alex', 'blake', 'casey'],
                description: 'Message role: system (project context), alex (product manager), blake (technical architect), casey (project manager)'
              },
              content: {
                type: 'string',
                description: 'Message content'
              }
            },
            required: ['role', 'content']
          }
        },
        project_metadata: {
          type: 'object',
          description: 'Optional project metadata',
          properties: {
            project_name: { type: 'string' },
            project_description: { type: 'string' },
            target_users: { type: 'string' },
            platform: { type: 'string' },
            timeline: { type: 'string' },
            team_size: { type: 'string' }
          }
        },
        use_full_context: {
          type: 'boolean',
          description: 'Use full context mode (recommended, default: true)',
          default: true
        }
      },
      required: ['consensus_messages']
    }
  },
  {
    name: 'get_backlog_summary',
    description: 'Get summary statistics from a generated backlog (epic count, story count, total hours, etc.)',
    inputSchema: {
      type: 'object',
      properties: {
        backlog: {
          type: 'object',
          description: 'Previously generated backlog object'
        }
      },
      required: ['backlog']
    }
  }
];

// ============================================================
// TOOL HANDLERS
// ============================================================

async function handleGenerateBacklog(args: Record<string, any>) {
  const { consensus_messages, project_metadata, use_full_context = true } = args;

  if (!consensus_messages || !Array.isArray(consensus_messages)) {
    throw new Error('consensus_messages is required and must be an array');
  }

  if (consensus_messages.length === 0) {
    throw new Error('consensus_messages cannot be empty');
  }

  // Call StoryCrafter service
  try {
    const response = await axios.post(
      `${STORYCRAFTER_SERVICE_URL}/generate-backlog`,
      {
        consensus_messages,
        project_metadata,
        use_full_context
      },
      {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 300000 // 5 minutes (generation can take time)
      }
    );

    if (!response.data.success) {
      throw new Error(response.data.error || 'Backlog generation failed');
    }

    return {
      content: [
        {
          type: 'text',
          text: JSON.stringify({
            success: true,
            backlog: response.data.backlog,
            summary: {
              total_epics: response.data.metadata.total_epics,
              total_stories: response.data.metadata.total_stories,
              total_estimated_hours: response.data.metadata.total_estimated_hours,
              generated_at: response.data.metadata.generated_at
            }
          }, null, 2)
        }
      ]
    };
  } catch (error: any) {
    if (error.response) {
      throw new Error(`StoryCrafter service error: ${error.response.data?.detail || error.response.statusText}`);
    } else if (error.request) {
      throw new Error(`StoryCrafter service unavailable: ${STORYCRAFTER_SERVICE_URL}`);
    } else {
      throw new Error(`Request error: ${error.message}`);
    }
  }
}

async function handleGetBacklogSummary(args: Record<string, any>) {
  const { backlog } = args;

  if (!backlog || typeof backlog !== 'object') {
    throw new Error('backlog is required and must be an object');
  }

  const summary = {
    project_name: backlog.project?.name || 'Unknown',
    total_epics: backlog.epics?.length || 0,
    total_stories: backlog.epics?.reduce((sum: number, epic: any) => sum + (epic.stories?.length || 0), 0) || 0,
    total_estimated_hours: backlog.epics?.reduce((sum: number, epic: any) => {
      return sum + (epic.stories?.reduce((storySum: number, story: any) => storySum + (story.estimated_hours || 0), 0) || 0);
    }, 0) || 0,
    epics_breakdown: backlog.epics?.map((epic: any) => ({
      id: epic.id,
      title: epic.title,
      story_count: epic.stories?.length || 0,
      total_hours: epic.stories?.reduce((sum: number, story: any) => sum + (story.estimated_hours || 0), 0) || 0
    })) || []
  };

  return {
    content: [
      {
        type: 'text',
        text: JSON.stringify(summary, null, 2)
      }
    ]
  };
}

// ============================================================
// MCP REQUEST HANDLER
// ============================================================

export async function POST(request: NextRequest) {
  try {
    const body: MCPRequest = await request.json();

    // Handle MCP protocol methods
    switch (body.method) {
      case 'tools/list':
        return NextResponse.json({
          tools: MCP_TOOLS
        });

      case 'tools/call':
        const toolName = body.params?.tool;
        const args = body.params?.arguments || {};

        let result;
        switch (toolName) {
          case 'generate_backlog':
            result = await handleGenerateBacklog(args);
            break;

          case 'get_backlog_summary':
            result = await handleGetBacklogSummary(args);
            break;

          default:
            return NextResponse.json(
              {
                error: {
                  code: -32601,
                  message: `Unknown tool: ${toolName}`
                }
              },
              { status: 400 }
            );
        }

        return NextResponse.json(result);

      default:
        return NextResponse.json(
          {
            error: {
              code: -32601,
              message: `Method not found: ${body.method}`
            }
          },
          { status: 400 }
        );
    }
  } catch (error: any) {
    console.error('MCP Error:', error);
    return NextResponse.json(
      {
        error: {
          code: -32603,
          message: error.message || 'Internal error'
        }
      },
      { status: 500 }
    );
  }
}

// Health check endpoint
export async function GET() {
  return NextResponse.json({
    name: 'StoryCrafter MCP',
    version: '1.0.0',
    description: 'AI-powered backlog generator for VISHKAR consensus',
    tools: MCP_TOOLS.map(t => t.name),
    service_url: STORYCRAFTER_SERVICE_URL,
    status: 'healthy'
  });
}
