
export interface DictInfo{
    name: string;
    path: string;
    root: string;
    css: string[];
    js: string[];
    data: string;
    cover: string;
}

export interface DictsInfo {
    [dict_name: string]: DictInfo;
}

export interface DictSettingInfo{
    id:string;
    name:string;
    cover_url:string;
    is_enabled: boolean;
}

export type DictsSettingInfo = DictSettingInfo[]


export interface SessionConfig {
    dictsSettingInfo: DictsSettingInfo;
}


export interface Message {
    message_id: number;
    raw_text: string;
    secondary_response: string | null;
    processed_html: string;
    time: string;
    role: 'user' | 'assistant' | 'system';
    is_playing: boolean;
}

export interface AIConfig {
    ai_avatar_url: string;
    base_url: string;
    api_key: string;
    model: string;
    temperature: number;
    max_tokens: number;
    context_max_tokens: number;
    max_messages: number;
    language: string;
    tts_voice: string;
    auto_play: boolean;
    auto_gen_title: boolean;
    show_separated_sentences: boolean;
    speech_rate: number;
    suggestions?: string[];
    secondary_prompt?: string;
    secondary_prompt_switch?: boolean;
}

