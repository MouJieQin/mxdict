import type { DictSettingInfo, SessionConfig } from '@/common/type-interface';
import { useSystemConfigStore } from '@/stores/stores'
const systemConfigStore = useSystemConfigStore();



const getDictSettingsForLookup = (dictsSettingOptionName: string) => {
    // return a list that contains the dict name which is not disabled in the same order.
    let dictnames: string[] = []
    systemConfigStore.systemConfig.dict_set_options[dictsSettingOptionName].filter((item: DictSettingInfo) => item.is_enabled).map(item => dictnames.push(item.name))
    return dictnames
}

const getDefaultSessionConfig = (sessionName: string) => {

    let sessionConfig: SessionConfig = {
        name: sessionName,
        default_folder: { "id": null },
        dictsSettingOptionName: "default",
        default_search_method: { "method": "prefix_search" },
        pin: { "is_pinned": true }
    }
    return sessionConfig
}


export { getDictSettingsForLookup, getDefaultSessionConfig }