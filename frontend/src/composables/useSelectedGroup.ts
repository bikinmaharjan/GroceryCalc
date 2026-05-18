import { ref } from 'vue'

export function useSelectedGroup() {
    const selectedGroup = ref(null)
    // Add logic here
    return { selectedGroup }
}
