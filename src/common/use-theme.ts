import { ref, watch } from 'vue';
import { useSystemConfigStore } from '@/stores/stores';

export const useTheme = () => {

    const systemConfigStore = useSystemConfigStore();

    watch(() => systemConfigStore.systemConfig?.appearance.theme, () => {
        updateTheme();
    })

    const getOperationSystemTheme = (): string => {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const operationSystemTheme = ref(getOperationSystemTheme());

    const updateTheme = () => {
        const theme = systemConfigStore.systemConfig?.appearance.theme;
        if (theme) {
            if (theme === 'auto') {
                const isDark = operationSystemTheme.value === 'dark';
                document.documentElement.classList.toggle('dark', isDark);
                systemConfigStore.setIsDark(isDark);
            } else {
                const isDark = theme === 'dark';
                document.documentElement.classList.toggle('dark', theme === 'dark');
                systemConfigStore.setIsDark(isDark);
            }
        }
    }

    // 初始化主题
    const initTheme = () => {
        updateTheme();
    };

    // 监听系统主题变化
    const watchSystemTheme = () => {
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            operationSystemTheme.value = e.matches ? 'dark' : 'light';
            const isDark = operationSystemTheme.value === 'dark';
            const theme = systemConfigStore.systemConfig?.appearance.theme;
            systemConfigStore.setIsDark(isDark);
            if (theme === 'auto') {
                document.documentElement.classList.toggle('dark', isDark);
            }
        });
    };

    return {
        initTheme,
        watchSystemTheme,
    };
};

