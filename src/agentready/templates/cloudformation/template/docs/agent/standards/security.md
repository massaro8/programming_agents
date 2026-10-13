# Static security baseline

Guard checks encryption presence, public access blocking, versioning, retention and unrestricted ingress. Bucket templates require at least one deny for plaintext S3 transport. This template-level baseline does not prove that every bucket has an associated policy or that Resource covers every bucket ARN; review per-bucket association, IAM least privilege and account-specific controls explicitly. Static checks never authorize deployment.
