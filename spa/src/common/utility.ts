import type { DictSettingInfo, DictsSettingInfo } from '@/common/type-interface';


const getDictSettingsForLookup = (dictsSetting: DictsSettingInfo) => {
    // return a list that contains the dict name which is not disabled in the same order.
    let dictnames: string[] = []
    dictsSetting.filter((item: DictSettingInfo) => item.is_enabled).map(item => dictnames.push(item.name))
    return dictnames
}


export { getDictSettingsForLookup }