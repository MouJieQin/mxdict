import type { DictSettingInfo } from '@/common/type-interface';
import { useSystemConfigStore } from '@/stores/stores'
const systemConfigStore = useSystemConfigStore();



const getDictSettingsForLookup = (dictsSettingOptionName: string) => {
    // return a list that contains the dict name which is not disabled in the same order.
    let dictnames: string[] = []
    systemConfigStore.systemConfig.dict_set_options[dictsSettingOptionName].filter((item: DictSettingInfo) => item.is_enabled).map(item => dictnames.push(item.name))
    return dictnames
}


export { getDictSettingsForLookup }