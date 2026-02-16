-- PostgreSQL Row-Level Security (RLS) Setup Script
-- This script prepares the database for cryptographically separated multi-tenancy.

-- 1. Enable RLS on sensitive tables
ALTER TABLE chatbot_app_chatsession ENABLE ROW LEVEL SECURITY;
ALTER TABLE chatbot_app_chatmessage ENABLE ROW LEVEL SECURITY;

-- 2. Create the RLS Policy for ChatSession
-- Only allow users to see/edit their own sessions
DROP POLICY IF EXISTS user_session_policy ON chatbot_app_chatsession;
CREATE POLICY user_session_policy ON chatbot_app_chatsession
    USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

-- 3. Create the RLS Policy for ChatMessage
-- Only allow users to see/edit their own messages
DROP POLICY IF EXISTS user_message_policy ON chatbot_app_chatmessage;
CREATE POLICY user_message_policy ON chatbot_app_chatmessage
    USING (user_id::text = current_setting('app.current_user_id', true))
    WITH CHECK (user_id::text = current_setting('app.current_user_id', true));

-- 4. Admin Policy (Optional)
-- Allow superusers to see everything
-- CREATE POLICY admin_all_policy ON chatbot_app_chatsession FOR ALL TO admins USING (true);

-- NOTE: In production, the application must set the 'app.current_user_id' setting 
-- inside the transaction that handles the request.
-- Example: SET LOCAL app.current_user_id = '123';
