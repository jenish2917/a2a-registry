import { RegistryClient } from './index';

async function main() {
    // Create a client instance
    const client = new RegistryClient({
        baseUrl: 'http://localhost:3000',
    });

    try {
        //1. Check registry health
        console.log('1. Checking registry health...');
        const health = await client.healthCheck();
        console.log('Health:', health);

        // 2. Register an agent
        console.log('\n2. Registering a translation agent...');
        const registration = await client.registerAgent({
            agentCard: {
                name: 'translation-agent',
                description: 'Multilingual translation agent',
                endpoint: 'https://translation-agent.example.com',
                protocolVersion: '0.3',
                capabilities: {
                    streaming: true,
                    pushNotifications: false,
                },
                skills: [
                    {
                        name: 'translate',
                        description: 'Translate text between languages',
                    },
                ],
            },
            tags: ['translation', 'nlp', 'language'],
            metadata: {
                version: '1.0.0',
                region: 'us-east-1',
            },
        });
        console.log('Registered:', registration);

        const agentId = registration.agentId;

        // 3. Get agent by ID
        console.log(`\n3. Getting agent ${agentId}...`);
        const agent = await client.getAgent(agentId);
        console.log('Agent:', agent);

        // 4. Send heartbeat
        console.log(`\n4. Sending heartbeat for ${agentId}...`);
        const heartbeat = await client.heartbeat(agentId);
        console.log('Heartbeat:', heartbeat);

        // 5. Search by skill
        console.log('\n5. Searching for agents with "translate" skill...');
        const translators = await client.searchBySkill('translate');
        console.log(`Found ${translators.length} translator(s)`);

        // 6. Search by tags
        console.log('\n6. Searching for agents with "nlp" tag...');
        const nlpAgents = await client.searchByTags(['nlp']);
        console.log(`Found ${nlpAgents.length} NLP agent(s)`);

        // 7. List all agents
        console.log('\n7. Listing all agents...');
        const allAgents = await client.listAgents({ limit: 10 });
        console.log(`Total agents: ${allAgents.total}`);

        // 8. Update agent
        console.log(`\n8. Updating agent ${agentId}...`);
        const updated = await client.updateAgent(agentId, {
            agentCard: {
                ...agent.agentCard,
                description: 'Enhanced multilingual translation agent',
            },
            tags: ['translation', 'nlp', 'language', 'enhanced'],
            metadata: {
                version: '1.1.0',
                region: 'us-east-1',
            },
        });
        console.log('Updated:', updated);

        // 9. Delete agent (cleanup)
        console.log(`\n9. Deleting agent ${agentId}...`);
        await client.deleteAgent(agentId);
        console.log('Agent deleted successfully');

        console.log('\n✅ All operations completed successfully!');
    } catch (error) {
        console.error('Error:', error);
        process.exit(1);
    }
}

main();
