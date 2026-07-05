import { useEffect } from 'react'
import { StatusBar } from 'expo-status-bar'
import { StyleSheet, View } from 'react-native'
import { NavigationContainer } from '@react-navigation/native'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { useFonts } from 'expo-font'
import { Inter_400Regular, Inter_500Medium, Inter_600SemiBold } from '@expo-google-fonts/inter'
import { JetBrainsMono_400Regular, JetBrainsMono_500Medium } from '@expo-google-fonts/jetbrains-mono'
import RootTabNavigator from './src/navigation/RootTabNavigator'
import { navigationTheme } from './src/navigation/navigationTheme'
import { colors } from './src/styles/tokens'
import { registerForPushNotificationsAsync } from './src/utils/notifications'
import { useResearchStore } from './src/store/useResearchStore'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

export default function App() {
  const [fontsLoaded] = useFonts({
    Inter_400Regular,
    Inter_500Medium,
    Inter_600SemiBold,
    JetBrainsMono_400Regular,
    JetBrainsMono_500Medium,
  })
  const setPushToken = useResearchStore((s) => s.setPushToken)

  // Best-effort: a denied permission or simulator (no physical device)
  // just means the Alerts feature stays unavailable, not an app crash.
  useEffect(() => {
    registerForPushNotificationsAsync()
      .then(setPushToken)
      .catch((err) => console.warn('Push notification registration skipped:', err.message))
  }, [setPushToken])

  if (!fontsLoaded) {
    return <View style={styles.loading} />
  }

  return (
    <QueryClientProvider client={queryClient}>
      <NavigationContainer theme={navigationTheme}>
        <RootTabNavigator />
        <StatusBar style="light" />
      </NavigationContainer>
    </QueryClientProvider>
  )
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    backgroundColor: colors.bgBase,
  },
})
