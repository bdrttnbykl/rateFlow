import { useState } from 'react'
import type { FormEvent } from 'react'
import './App.css'

const currencies = ['USD', 'EUR', 'TRY', 'GBP'] as const
const API_URL = '/convert'

type Currency = (typeof currencies)[number]

type ConvertResponse = {
  amount: number
  base: Currency
  quote: Currency
  rate: number
  result: number
  date: string
}

function App() {
  const [base, setBase] = useState<Currency>('USD')
  const [quote, setQuote] = useState<Currency>('TRY')
  const [amount, setAmount] = useState<string>('100')
  const [result, setResult] = useState<ConvertResponse | null>(null)
  const [error, setError] = useState<string>('')
  const [isLoading, setIsLoading] = useState<boolean>(false)

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setIsLoading(true)
    setError('')

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          base,
          quote,
          amount: Number(amount),
        }),
      })

      const data = (await response.json()) as ConvertResponse | { error: string }

      if (!response.ok || 'error' in data) {
        throw new Error('error' in data ? data.error : 'Donusum basarisiz oldu')
      }

      setResult(data)
    } catch (submitError) {
      setResult(null)
      setError(
        submitError instanceof Error
          ? submitError.message
          : 'Sunucu ile baglanti kurulamadi',
      )
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <section className="hero-panel">
        <p className="eyebrow">RateFlow</p>
        <h1>TypeScript tabanli canli doviz cevirici</h1>
        <p className="hero-copy">
          React arayuzu Flask backend&apos;ine istek atar ve guncel kuru tek bir
          ekranda gosterir.
        </p>
      </section>

      <section className="converter-panel">
        <form className="converter-form" onSubmit={handleSubmit}>
          <label>
            Tutar
            <input
              min="0"
              step="0.01"
              type="number"
              value={amount}
              onChange={(event) => setAmount(event.target.value)}
              placeholder="100"
              required
            />
          </label>

          <label>
            Baz para birimi
            <select
              value={base}
              onChange={(event) => setBase(event.target.value as Currency)}
            >
              {currencies.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </label>

          <label>
            Hedef para birimi
            <select
              value={quote}
              onChange={(event) => setQuote(event.target.value as Currency)}
            >
              {currencies.map((currency) => (
                <option key={currency} value={currency}>
                  {currency}
                </option>
              ))}
            </select>
          </label>

          <button className="submit-button" type="submit" disabled={isLoading}>
            {isLoading ? 'Hesaplaniyor...' : 'Cevir'}
          </button>
        </form>

        {error ? <p className="status-card error">{error}</p> : null}

        {result ? (
          <article className="result-card">
            <p className="result-label">Sonuc</p>
            <h2>
              {result.amount} {result.base} = {result.result} {result.quote}
            </h2>
            <p>Kur: 1 {result.base} = {result.rate} {result.quote}</p>
            <p>Tarih: {result.date}</p>
          </article>
        ) : (
          <article className="status-card">
            Ilk donusumu yapmak icin tutari girip formu gonder.
          </article>
        )}
      </section>
    </main>
  )
}

export default App
