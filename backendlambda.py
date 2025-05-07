// Coveo Bedrock Agent Action Lambda
exports.handler = async (event) => {
    console.log('Incoming event:', JSON.stringify(event, null, 2));
    
    try {
        // Extract API path and parameters
        const apiPath = event.apiPath;
        const parameters = event.parameters || {};
        
        // Process based on path
        let response;
        
        switch (apiPath) {
            case '/Name':
                console.log('Processing Name search request');
                response = await handleNameSearch(parameters);
                break;
            case '/PolicyExpert':
                console.log('Processing Policy Expert search request');
                response = await handleSharedEndpoint(parameters, 'policy');
                break;
            case '/Developer':
                console.log('Processing Developer search request');
                response = await handleSharedEndpoint(parameters, 'developer');
                break;
            case '/Crew':
                console.log('Processing Crew search request');
                response = await handleSharedEndpoint(parameters, 'crew');
                break;
            default:
                throw new Error(`Unsupported API path: ${apiPath}`);
        }
        
        // Return formatted response for Bedrock Agent
        return {
            actionGroup: event.actionGroup,
            apiPath: event.apiPath,
            httpMethod: event.httpMethod,
            httpStatusCode: 200,
            responseBody: JSON.stringify(response)
        };
    } catch (error) {
        console.error('Error processing request:', error);
        
        // Return error response
        return {
            actionGroup: event.actionGroup,
            apiPath: event.apiPath,
            httpMethod: event.httpMethod,
            httpStatusCode: error.statusCode || 500,
            responseBody: JSON.stringify({
                error: error.message,
                details: error.details || 'An unexpected error occurred'
            })
        };
    }
};

/**
 * Handles employee search by name
 * This uses a different Coveo API endpoint than the other functions
 */
async function handleNameSearch(parameters) {
    console.log('Name search parameters:', parameters);
    
    // Validate required parameters
    if (!parameters.name) {
        throw createError(400, 'Name parameter is required');
    }
    
    try {
        // Make API call to Coveo employee directory API
        // This would be your actual implementation to call Coveo API
        // const apiResponse = await callCoveoEmployeeAPI(parameters.name);
        
        // For demonstration, using mock data
        const employeeData = await mockEmployeeSearch(parameters.name);
        
        // Format response as per diagram specifications
        return {
            ...employeeData,
            // Add any additional formatting needed for ECS forms
            _metadata: {
                responseType: 'EMPLOYEE_INFO',
                source: 'Coveo Employee Directory'
            }
        };
    } catch (err) {
        console.error('Error in employee search:', err);
        throw createError(500, 'Failed to retrieve employee information', err);
    }
}

/**
 * Handles the three similar API endpoints (PolicyExpert, Developer, Crew)
 * These all use the same Coveo API but with different search parameters
 */
async function handleSharedEndpoint(parameters, type) {
    console.log(`Processing ${type} request with parameters:`, parameters);
    
    // Validate required parameters
    if (!parameters.query) {
        throw createError(400, 'Query parameter is required');
    }
    
    try {
        // Prepare payload based on endpoint type
        const payload = prepareSearchPayload(parameters, type);
        
        // Make API call to shared Coveo search API
        // This would be your actual implementation to call Coveo API
        // const apiResponse = await callCoveoSearchAPI(payload);
        
        // For demonstration, using mock data
        const searchResults = await mockSharedSearch(payload);
        
        // Format the response for ECS as shown in the diagram
        return formatECSResponse(searchResults, type);
    } catch (err) {
        console.error(`Error in ${type} search:`, err);
        throw createError(500, `Failed to retrieve ${type} information`, err);
    }
}

/**
 * Prepares the search payload based on endpoint type
 */
function prepareSearchPayload(parameters, type) {
    // Base payload with common parameters
    const payload = {
        query: parameters.query,
        searchType: type,
        maxResults: 5
    };
    
    // Add type-specific parameters
    switch (type) {
        case 'policy':
            if (parameters.department) payload.department = parameters.department;
            payload.contentTypes = ['policy', 'guideline', 'procedure'];
            break;
            
        case 'developer':
            if (parameters.technology) payload.technology = parameters.technology;
            payload.contentTypes = ['documentation', 'codeExample', 'api'];
            break;
            
        case 'crew':
            if (parameters.project) payload.project = parameters.project;
            payload.contentTypes = ['team', 'project', 'organization'];
            break;
    }
    
    return payload;
}

/**
 * Formats response for ECS forms and buttons
 */
function formatECSResponse(results, type) {
    // Base response object
    const formattedResponse = {
        results: results.items || [],
        formattedResponse: {
            title: `${capitalizeFirstLetter(type)} Search Results`,
            description: `Found ${results.items.length} results for your query`,
            items: []
        }
    };
    
    // Format items for display
    formattedResponse.formattedResponse.items = results.items.map(item => {
        return {
            title: item.title,
            description: item.description,
            metadata: item.metadata || {}
        };
    });
    
    // Add ECS buttons as shown in the diagram
    formattedResponse.formattedResponse.buttons = [
        { text: "More Details", value: "more_details" },
        { text: "New Search", value: "new_search" }
    ];
    
    return formattedResponse;
}

/**
 * Helper to create standardized error objects
 */
function createError(statusCode, message, originalError = null) {
    const error = new Error(message);
    error.statusCode = statusCode;
    if (originalError) {
        error.details = originalError.message;
    }
    return error;
}

/**
 * Helper to capitalize first letter of a string
 */
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}

// Mock functions for demonstration
async function mockEmployeeSearch(name) {
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 100));
    
    return {
        fname: "John",
        lastname: "Smith",
        businessTitle: "Senior Software Engineer",
        departmentName: "Engineering",
        locationName: "Seattle",
        crewId: "EMP12345",
        email: "john.smith@company.com",
        managerName: "Jane Doe",
        managerCrewId: "EMP67890"
    };
}

async function mockSharedSearch(payload) {
    // Simulate API latency
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Different mock results based on search type
    const items = [];
    
    for (let i = 1; i <= 3; i++) {
        const item = {
            id: `result-${i}`,
            title: `${payload.searchType.toUpperCase()} Result ${i}`,
            description: `This is a sample ${payload.searchType} result for query: ${payload.query}`
        };
        
        // Add type-specific fields
        if (payload.searchType === 'policy') {
            item.policyType = ['Corporate', 'HR', 'Security'][i % 3];
            item.lastUpdated = '2025-03-01';
        } else if (payload.searchType === 'developer') {
            item.language = ['Python', 'JavaScript', 'Java'][i % 3];
            item.platform = ['AWS', 'Azure', 'GCP'][i % 3];
        } else if (payload.searchType === 'crew') {
            item.teamSize = (i * 5) + 3;
            item.location = ['Seattle', 'New York', 'Remote'][i % 3];
        }
        
        items.push(item);
    }
    
    return { items };
}
