import { WebSocketService } from '@/common/websocket-client'

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
    sendLookupKeyword(keyword: string) {
        this._send(
            'lookup_keyword',
            {
                keyword: keyword,
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

    sendKeywordOptionsSearch(keyword: string) {
        this._send(
            'keyword_options_search',
            {
                keyword: keyword,
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
