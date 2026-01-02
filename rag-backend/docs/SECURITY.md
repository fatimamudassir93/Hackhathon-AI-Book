# API Key Security and Key Rotation Guide

This document outlines security best practices for API key handling and key rotation procedures for the Physical AI Book RAG system.

## Table of Contents
1. [API Key Security](#api-key-security)
2. [Environment Variable Management](#environment-variable-management)
3. [Key Rotation Procedures](#key-rotation-procedures)
4. [Monitoring and Auditing](#monitoring-and-auditing)
5. [Incident Response](#incident-response)

## API Key Security

### Current API Keys Used

The system uses the following API keys:

- `QDRANT_API_KEY` - For Qdrant Cloud access
- `GROQ_API_KEY` - For LLM access via Groq
- `COHERE_API_KEY` - For embedding generation via Cohere

### Security Best Practices

#### 1. Storage
- Store API keys in environment variables, never in source code
- Use `.env` files that are git-ignored for local development
- Use secure secret management in production environments (AWS Secrets Manager, Azure Key Vault, etc.)

#### 2. Access Control
- Follow the principle of least privilege when creating API keys
- Limit API key permissions to only necessary operations
- Use separate API keys for different environments (dev, staging, prod)

#### 3. Transmission
- Always use HTTPS/TLS for API calls
- API keys are transmitted in headers, ensure transport security
- Never log API keys or include them in error messages

## Environment Variable Management

### Local Development
1. Create a `.env` file in the `rag-backend/` directory
2. Add your API keys following the format:
```bash
QDRANT_API_KEY=your_qdrant_api_key
GROQ_API_KEY=your_groq_api_key
COHERE_API_KEY=your_cohere_api_key
```
3. Ensure `.env` is in your `.gitignore` file

### Production Deployment
1. Use your platform's secret management system
2. For Docker: Use `--env-file` or Docker secrets
3. For Kubernetes: Use Secret objects
4. For cloud platforms: Use their native secret management services

## Key Rotation Procedures

### Scheduled Rotation
- Rotate API keys every 90 days for production systems
- Rotate keys immediately if a security incident occurs
- Plan rotations during low-usage periods to minimize disruption

### Rotation Steps

#### 1. Before Rotation
- Document current key usage and permissions
- Ensure backup access methods are available
- Schedule rotation during maintenance window if needed

#### 2. Rotation Process
1. Generate new API keys in the respective services
2. Update environment variables/secrets in your deployment
3. Restart applications to load new keys
4. Test functionality with new keys
5. Wait 24 hours to ensure stability
6. Deactivate/expire old keys in the service provider

#### 3. After Rotation
- Verify all systems are working with new keys
- Update documentation with rotation date
- Notify team members of the change if necessary

### Automated Rotation
Consider implementing automated key rotation:
- Use cloud provider tools (AWS Secrets Manager rotation)
- Implement monitoring to alert before expiration
- Create scripts to automate the rotation process

## Monitoring and Auditing

### API Key Usage Monitoring
- Monitor API call volumes for unusual patterns
- Set up alerts for unexpected usage spikes
- Track which services are using each key

### Audit Trail
- Log API key usage with timestamps (without logging the actual keys)
- Monitor for unauthorized access attempts
- Regularly review access logs for anomalies

### Alerting
Set up alerts for:
- Unusual API usage patterns
- Failed authentication attempts
- Key expiration warnings (if applicable)

## Incident Response

### If an API Key is Compromised

1. **Immediate Actions (within 5 minutes)**
   - Rotate the compromised key immediately
   - Review recent usage logs
   - Assess potential impact

2. **Short-term Actions (within 1 hour)**
   - Update all systems with new key
   - Restart affected services
   - Monitor for continued unauthorized access

3. **Long-term Actions (within 24 hours)**
   - Conduct security review
   - Implement additional security measures if needed
   - Document incident and lessons learned

### Security Measures to Implement
- Use separate keys for different services/applications
- Implement rate limiting to reduce impact of key misuse
- Monitor for data exfiltration attempts
- Regular security audits of key management

## Development vs Production Security

### Development
- Use dedicated development API keys with limited permissions
- Do not use production keys in development environments
- Implement the same security practices in development

### Production
- Use production-grade API keys with minimal necessary permissions
- Implement comprehensive monitoring
- Have incident response procedures ready

## Additional Security Recommendations

1. **Network Security**
   - Restrict API key access by IP address where possible
   - Use VPN or private networks for sensitive operations

2. **Application Security**
   - Validate and sanitize all inputs that might affect API calls
   - Implement proper error handling without exposing sensitive information
   - Regular security testing and code reviews

3. **Access Management**
   - Regularly review who has access to API keys
   - Use role-based access control
   - Remove access when team members leave

## Compliance Considerations

- Ensure API key handling meets relevant compliance requirements (GDPR, HIPAA, etc.)
- Maintain audit logs as required by compliance standards
- Regular security assessments
- Data protection impact assessments if applicable