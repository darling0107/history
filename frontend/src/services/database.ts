import { supabase } from './supabase'
import type { Database } from './supabase'

type UserProfile = Database['public']['Tables']['user_profiles']['Row']
type LessonProgress = Database['public']['Tables']['lesson_progress']['Row']
type ChatHistory = Database['public']['Tables']['chat_history']['Row']

// User Profile Operations
export async function getUserProfile(userId: string): Promise<UserProfile | null> {
  const { data, error } = await supabase.from('user_profiles').select('*').eq('id', userId).single()

  if (error) {
    console.error('Error fetching user profile:', error)
    return null
  }

  return data
}

export async function updateUserProfile(
  userId: string,
  updates: Partial<UserProfile>,
): Promise<boolean> {
  const { error } = await supabase
    .from('user_profiles')
    .update({
      ...updates,
      updated_at: new Date().toISOString(),
    })
    .eq('id', userId)

  if (error) {
    console.error('Error updating user profile:', error)
    return false
  }

  return true
}

// Lesson Progress Operations
export async function getLessonProgress(userId: string): Promise<LessonProgress[]> {
  const { data, error } = await supabase.from('lesson_progress').select('*').eq('user_id', userId)

  if (error) {
    console.error('Error fetching lesson progress:', error)
    return []
  }

  return data || []
}

export async function saveLessonProgress(
  userId: string,
  lessonId: string,
  completed: boolean,
  score?: number,
): Promise<boolean> {
  const { error } = await supabase.from('lesson_progress').upsert({
    user_id: userId,
    lesson_id: lessonId,
    completed,
    score,
    completed_at: completed ? new Date().toISOString() : null,
  })

  if (error) {
    console.error('Error saving lesson progress:', error)
    return false
  }

  return true
}

// Chat History Operations
export async function getChatHistory(userId: string, figureId?: string): Promise<ChatHistory[]> {
  let query = supabase.from('chat_history').select('*').eq('user_id', userId)

  if (figureId) {
    query = query.eq('figure_id', figureId)
  }

  const { data, error } = await query.order('updated_at', { ascending: false })

  if (error) {
    console.error('Error fetching chat history:', error)
    return []
  }

  return data || []
}

export async function saveChatHistory(
  userId: string,
  figureId: string,
  messages: Record<string, unknown>[],
): Promise<boolean> {
  const { error } = await supabase.from('chat_history').upsert({
    user_id: userId,
    figure_id: figureId,
    messages,
    updated_at: new Date().toISOString(),
  })

  if (error) {
    console.error('Error saving chat history:', error)
    return false
  }

  return true
}

export async function deleteChatHistory(userId: string, figureId: string): Promise<boolean> {
  const { error } = await supabase
    .from('chat_history')
    .delete()
    .eq('user_id', userId)
    .eq('figure_id', figureId)

  if (error) {
    console.error('Error deleting chat history:', error)
    return false
  }

  return true
}

// User Preferences Operations
export async function getUserPreferences(userId: string): Promise<Record<string, unknown>> {
  const { data, error } = await supabase
    .from('user_preferences')
    .select('preferences')
    .eq('user_id', userId)
    .single()

  if (error) {
    console.error('Error fetching user preferences:', error)
    return {}
  }

  return data?.preferences || {}
}

export async function saveUserPreferences(
  userId: string,
  preferences: Record<string, unknown>,
): Promise<boolean> {
  const { error } = await supabase.from('user_preferences').upsert({
    user_id: userId,
    preferences,
    updated_at: new Date().toISOString(),
  })

  if (error) {
    console.error('Error saving user preferences:', error)
    return false
  }

  return true
}
