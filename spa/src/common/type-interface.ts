

// export interface LookupKeywordMsg {
//     dict_name
// }



export interface SentenceInfo {
    text: string;
    messageId: number;
    sentenceId: number;
    isHeading?: boolean;
}

// 处理结果接口
export interface ProcessResult {
    html: string;
    sentences: SentenceInfo[];
}



export interface Message {
    message_id: number;
    raw_text: string;
    secondary_response: string | null;
    processed_html: string;
    sentences: Array<SentenceInfo>;
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

