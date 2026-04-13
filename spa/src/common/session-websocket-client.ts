import { WebSocketService } from '@/common/websocket-client'
import type { DictsSettingInfo } from '@/common/type-interface'

class SessionWebSocketService extends WebSocketService {
    constructor(url: string) {
        super(url)
    }

    private _send(type: string, data: {} | null = null) {
        this.send({
            type: type,
            data: {
                ...data,
            },
        })
    }

    // 发送用户输入
    sendLookupKeyword(keyword: string, dictSettings: string[] | null = null) {
        this._send(
            'lookup_keyword',
            {
                keyword: keyword,
                dict_settings: dictSettings,
            }
        )
    }

    sendSessionDictSettings(settings: DictsSettingInfo) {
        this._send(
            'session_dict_settings',
            {
                settings: settings,
            }
        )
    }

    sendFloatingWindowPinClick(sessionId: number) {
        this._send(
            'toggle_floating_pin',
            {
                session_id: sessionId
            }
        )
    }

    sendKeywordOptionsSearch(keyword: string, searchMethod: string = 'prefix_search', dictSettings: string[] | null = null) {
        this._send(
            'keyword_options_search',
            {
                keyword: keyword,
                search_method: searchMethod, // 使用传入的搜索方法
                dict_settings: dictSettings, // 使用传入的字典设置
            }
        )
    }


    sendToggleFloatingWindowPin(fullPath: string) {
        this._send('toggle_float_pin', {
            full_path: fullPath,
        })
    }


}

// 导出单例或工厂函数，根据项目需求选择
let sessionWebSocketInstance: SessionWebSocketService | null = null;
export function useSessionWebSocket(id: number) {
    sessionWebSocketInstance = new SessionWebSocketService("ws://localhost:5959/ws/dictionary/session/" + id);
    return sessionWebSocketInstance;
}
export { SessionWebSocketService }
