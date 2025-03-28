# prompts.py

# Промпт для поиска компаний, разрабатывающих или владеющих софтом
PROMPT_SOFTWARE = """
Determine if the company develops or owns proprietary software.

### Relevant if:
- The company **develops or owns** proprietary software.
  - Examples: Standalone Software, SaaS, Embedded Software, API, ERP, CRM, CAD, AI-based solutions, or analytics platforms.
- The company **sells, licenses, or distributes** its software as a product.

### Not Relevant if:
- The company is an **IT service provider**, including:
  - Custom software development firms, IT outsourcing, managed IT services.
  - System integrators, technology consulting firms.
- The company is a **reseller or distributor of third-party IT solutions** (e.g., Microsoft 365, Salesforce, SAP, Shopify).
- The company **develops Open Source software** as its primary product or business model.
- The company **develops or publishes video games**, gaming platforms, or related entertainment software.

### Output format:
- If relevant: `+ Relevant -` followed by a **concise and engaging** explanation of what software product or platform the company offers (**max 10 words**). Examples:
  - `+ Relevant - AI-powered analytics for finance.`
  - `+ Relevant - Cloud ERP for supply chains.`
  - `+ Relevant - CRM for automated sales.`
- If not relevant: `- Not Relevant`

**Content:**  
{content}
"""
# Промпт для поиска крупных предприятий (больницы, заводы, поставщики) без ИТ-услуг
PROMPT_ENTERPRISES = """
Determine if the company meets the following criteria based on its website content.

### Relevant if:
- The company **develops or owns proprietary software**.
- The company is a **large enterprise, supplier, manufacturer, distributor, hospital, or operates in a non-IT industry**.
- The company **is not an IT service provider, online retailer, or marketplace**.

### Not Relevant if:
- The company is an **IT service provider**, including:
  - Custom software development firms, IT outsourcing, system integrators.
- The company is an **online store, e-commerce platform, marketplace, or digital retail service**.
- The company **resells third-party IT solutions** (e.g., Microsoft 365, Salesforce, SAP, Shopify).
- The company **develops Open Source software** as its primary product or business model.
- The company **develops or publishes video games**, gaming platforms, or related entertainment software.
- The company is a **religious organization** or operates with religious affiliations.
- The company is a **military organization**, defense contractor, or provides military-related products or services.
- The company operates in the **space industry**, including space exploration, satellite technology, or aerospace research.
- The company is a **non-profit organization**, charity, or operates with non-profit objectives.

### Output format:
- If relevant: `+ Relevant - {Short explanation of why the company qualifies}`
- If not relevant: `- Not Relevant`

**Content:**  
{content}
"""

PROMPT_SIGNALS = """
Determine if the company develops or owns proprietary software and extract key signals.

### Relevant if:
- The company **develops or owns** proprietary software.
  - Examples: Standalone Software, SaaS, Embedded Software, API, ERP, CRM, CAD, AI-based solutions, or analytics platforms.
- The company **sells, licenses, or distributes** its software as a product.

### Not Relevant if:
- The company is an **IT service provider**, including:
  - Custom software development firms, IT outsourcing, managed IT services.
  - System integrators, technology consulting firms.
- The company is a **reseller or distributor of third-party IT solutions** (e.g., Microsoft 365, Salesforce, SAP, Shopify).
- The company **develops Open Source software** as its primary product or business model.
- The company **develops or publishes video games**, gaming platforms, or related entertainment software.

### Output format:
- If relevant: `+ Relevant - {Short explanation of why the company qualifies} | Key Signals: {Extracted Signals}`
- If not relevant: `- Not Relevant`

### Extracted Signals:
- **Product Type**: SaaS, ERP, CRM, CAD, AI-based solution, API, analytics platform, etc.
- **Industry Focus**: Manufacturing, Healthcare, FinTech, etc.
- **Unique Features**: AI-powered, cloud-based, automation-driven, cybersecurity-focused, etc.
- **Recent News** (if available): New product launch, funding, acquisitions, partnerships.

**Content:**  
{content}
"""
