import { ref } from 'vue'

export function useSelectedGroup() {
    const selectedGroup = ref<{ id: number; name: string } | null>(null)
    // Add logic here
    return { selectedGroup }
}
