# SOC Analyst Project — Management Briefing

## Wnioski (Findings)
1. **Krajobraz ataków:** Najczęstszymi wektorami ataków w analizowanym okresie były *Brute Force* (170 incydentów) oraz *Phishing* (139 incydentów). Charakteryzują się one jednak niską skutecznością przełamań na poziomie około 6.4%.
2. **Skuteczność ataków:** Największe zagrożenie stanowiły ataki *DDoS* (95 incydentów, 20% skuteczności) oraz *SQL Injection* (89 incydentów, 13.5% skuteczności). Średni czas reakcji SOC na ataki DDoS wynosił ponad 33 minuty.
3. **Zagrożenie zasobów (Assets):** Najbardziej podatnym zasobem infrastruktury okazał się *Web Server*. Przyjął 179 ataków, z czego aż 30 zakończyło się kompromitacją. Zidentyfikowano również powtarzające się ataki z adresu IP `192.0.2.10`, który wygenerował 117 zdarzeń, prowadząc do 10 włamań.

## Zasób wymagający dalszego śledztwa
**Web Server:** Ze względu na najwyższą liczbę udanych przełamań (30 skompromitowanych incydentów), zasób ten wymaga pilnego audytu. Należy przeanalizować logi dostępowe i reguły zapory, aby ustalić, dlaczego obecne mechanizmy ochrony nie zablokowały szkodliwego ruchu (szczególnie w przypadku SQL Injection).

## Rekomendacja operacyjna
Należy wdrożyć zautomatyzowane reguły blokujące (Firewall/WAF) dla adresów IP generujących największy i powtarzalny ruch sieciowy (np. `192.0.2.10`). Zmniejszy to wolumen incydentów typu DDoS i zredukuje czas reakcji analityków SOC.

## Ograniczenia analizy
Kraje pochodzenia widoczne w zbiorze danych stanowią wyłącznie metadane powiązane z adresami IP. Atakujący powszechnie wykorzystują infrastrukturę proxy i sieci VPN, w związku z czym na podstawie tych danych nie można z całą pewnością przypisać odpowiedzialności za ataki określonym państwom.