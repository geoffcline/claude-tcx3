from main import SERVICE_NAME
import json


def generate_abstract(bedrock, content, filename):
    print(f"Generating abstract for {filename}...")
    prompt = f"""Create a concise abstract for a documentation section. The abstract should not exceed 160 characters.

Context: This is a section of a technical documentation website for {SERVICE_NAME}. Filename: {filename}

Instructions:
1. Analyze the content thoroughly.
2. Identify the main topic, key arguments, and significant conclusions.
3. Create an abstract that:
   - Clearly states the primary subject
   - Uses language that aids in search and discovery
   - Avoids jargon but includes important terminology
   - Is 2 sentences, if possible, or 1. 
   - Avoids marketing speak. 
   - Uses as many keywords as possible for SEO

Do: focus abstracts on customer needs: Start the sentence with verbs like learn, create, or use.
Don't phrase an abstract around what the product allows, enables, or lets customers do.

Example of customer-focused "Do" abstract:
Learn how to <do or use something> to <get benefit> with <ServiceName/feature>.

Example of customer-focused "Know" abstract:
Discover how <ServiceName console> components work to <do what the customer needs>.

Good abstract: Learn how to view your quota history and request a quota increase in the AWS Management Console.
Good abstract: Use allocation strategies to manage how Auto Scaling fulfills On-Demand and Spot capacities from the multiple instance types.

Important: Provide ONLY the abstract text, without any additional formatting, headings, or metadata.

Markdown Content:
{content}  # Using entire content as requested

Abstract:"""

    body = json.dumps({
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}],
        "anthropic_version": "bedrock-2023-05-31"
    })

    print("Sending request to Bedrock for abstract generation...")
    response = bedrock.invoke_model(body=body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")
    print("Received response from Bedrock.")

    response_body = json.loads(response.get("body").read())
    abstract = response_body.get("content", [{}])[0].get("text", "").strip()
    print(f"Generated abstract of {len(abstract)} characters.")
    return abstract


def generate_new_title(bedrock, original_title, abstract):
    print(f"Generating new title based on original title: {original_title}")
    prompt = f"""Generate a new title for a {SERVICE_NAME} technical documentation page based on the following guidelines:

    1. Length: 40-70 characters, preferring shorter titles when possible
    2. Style: Clear, concise, and appropriate for technical documentation
    3. Focus: Customer-centric, reflecting specific scenarios or tasks
    4. Format: 
       - Avoid using colons (:)
       - Avoid two-part titles (e.g., "Creating an Amazon EKS Cluster: A Step-by-Step Guide")
    5. Context: Specific to {SERVICE_NAME} services and features

    Prime Example:
    - Original: "Horizontal Pod Autoscaler"
      New: "Auto-scaling Kubernetes Pods with Horizontal Pod Autoscaler"

    Examples:
    - Original: "Behaviors"
      New: "Configuring Security Profile Behaviors using Rules Detect or ML Detect"
    - Original: "Job Definition Parameters"
      New: "Setting Up Job Definition Parameters"
    - Original: "Amazon EKS ended support for Dockershim"
      New: "Migrating from Dockershim to containerd"
    - Original: "Amazon EKS optimized AMIs"
      New: "Deploy Nodes with Amazon EKS Optimized AMIs"

    Avoid "Managing". 
    - Avoid: Managing Job Dependencies in AWS Batch
    - Avoid: Managing Long-Running Job Timeouts with AWS Batch
    Instead of "Managing" think of the abstract and why someone might want to use this feature. 
    What task are they looking to do?

    Input:
    Original Title: {original_title}
    Abstract: {abstract}

    Output:
    Provide only the new title, without any additional text or formatting.
    """

    body = json.dumps({
        "max_tokens": 256,
        "messages": [{"role": "user", "content": prompt}],
        "anthropic_version": "bedrock-2023-05-31"
    })

    print("Sending request to Bedrock for title generation...")
    response = bedrock.invoke_model(body=body, modelId="anthropic.claude-3-sonnet-20240229-v1:0")
    print("Received response from Bedrock.")

    response_body = json.loads(response.get("body").read())
    new_title = response_body.get("content", [{}])[0].get("text", "").strip()
    print(f"Generated new title: {new_title}")
    return new_title
