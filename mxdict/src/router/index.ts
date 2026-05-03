import { createRouter, createWebHashHistory, type RouteRecordRaw } from 'vue-router'

// 懒加载组件
const Dict = () => import('@/views/DictPage.vue')
const Home = () => import('@/views/Home.vue')

const routes: RouteRecordRaw[] = [
    {
        path: '/',
        component: () => import('@/views/DictLayout.vue'),
        children: [
            {
                path: '',
                name: 'Home',
                component: Home
            },
            {
                path: 'dict/:id',
                name: 'Dict',
                component: Dict
            }
        ]
    },
]

const router = createRouter({
    history: createWebHashHistory(),
    routes
})

export default router
