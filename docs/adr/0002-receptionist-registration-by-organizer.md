# Receptionist accounts are registered by organizers, not admins

Self-service registration accepts only CUSTOMER and ORGANIZER roles. A
RECEPTIONIST account can only be created through the same register endpoint by
an authenticated user whose role is ORGANIZER. We chose this over Django-admin
provisioning so the demo flow works end-to-end without admin access, and over
fully-open registration because receptionists are trusted validators tied to an
organizer's operation.

Consequences: role selection at `/api/auth/register/` is context-sensitive;
the serializer raises 403 when an unauthenticated or non-organizer caller
requests the RECEPTIONIST role. Email and role are immutable afterwards.
