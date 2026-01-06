def build_prompt(controls: dict, description: str, user_details: dict = None) -> str:
    """
    Constructs the LLM prompt with strict JSON formatting instructions.
    """
    # 1. Basic Controls
    tone = controls.get("tone", "professional")
    length = controls.get("length", "medium")
    recipient = controls.get("recipient", "Recipient")
    
    # Default to empty dict if None
    user_details = user_details or {}

    # 2. Dynamic Signature & Role Logic
    role = user_details.get("role", "professional")
    name = user_details.get("name", "")
    
    # Start with just the name
    sig_block = f"{name}"
    
    # Add details based on the selected Role
    if role == "student" and user_details.get("university"):
        sig_block += f"\nStudent, {user_details['university']}"
        
    elif role == "professional" and user_details.get("company"):
        # Use title if provided, otherwise default to "Employee"
        title = user_details.get("title") or "Employee"
        sig_block += f"\n{title}, {user_details['company']}"
        
    elif role == "business" and user_details.get("company"):
        sig_block += f"\nOwner, {user_details['company']}"

    # Always add email if present
    if user_details.get("email"):
        sig_block += f"\n{user_details['email']}"
            
    # Create the mandatory instruction string
    signature_instruction = f"""
    MANDATORY SIGNATURE RULE:
    The 'closing' field must end with a professional sign-off (like 'Best regards,'), followed by a newline, and then this EXACT signature block:
    {sig_block}
    """

    # 3. System Persona Logic (The "Brain" Shift)
    system_role = "expert professional email writer"
    if role == "student":
        system_role = "polite university student"
    elif role == "business":
        system_role = "experienced business owner"

    # 4. Final Prompt Construction
    return f"""
You are a {system_role}. 
Your task is to write a {tone}, {length}-length email to {recipient}.

OUTPUT FORMAT RULES:
1. Return ONLY a raw JSON object. 
2. Do not include markdown formatting (no ```json ... ```).
3. Keys must be: "subject", "greeting", "body", "closing".
4. "subject": Max 100 chars. No placeholders.
5. "greeting": Professional greeting.
6. "body": Clear, concise, NO placeholders.
7. "closing": Professional sign-off followed by the signature.
{signature_instruction}

USER REQUEST:
{description}
"""