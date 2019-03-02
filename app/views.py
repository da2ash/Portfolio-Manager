from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import Sign
import tweepy
from textblob import TextBlob
from .models import Company
import numpy as np
import os
from keras.models import Sequential
from keras.layers import Dense

consumer_key = "k3pEbBjtma2rzFUOebGxaSKq0"
consumer_secret = "gF8u5ypWPr2EMNTfhujEI4X9uWlM1ROv6dxWzCHOMkmbjKBOU4"
access_token = "1101314053589233664-Ahed5wAS2hDCqdcnV40J6eCYgnRNOv"
access_token_secret = "GNOhScWWbhpBn4F5lwSlIqviHe8UCfE7J80mlGOnqqRja"


def get_sentiment(company_name):
    print("HERE")
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)
    public_tweets = api.search(company_name, count=50)
    positive, null = 0, 0

    for tweet in public_tweets:
        blob = TextBlob(tweet.text).sentiment
        if blob.subjectivity == 0:
            null += 1
            next
        if blob.polarity > 0:
            positive += 1

    if positive > (len(public_tweets) - null) / 2:
        return True
    else:
        return False


def predictor(ticker):
    base = os.getcwd()
    path = base + '/app/data/' + ticker + '.csv'
    fd = open(path)
    dataset = []
    for n, line in enumerate(fd):
        if n != 0:
            dataset.append(float(line.split(',')[4]))
    dataset = np.array(dataset)

    def create_dataset(dataset):
        data_x = [dataset[n + 1] for n in range(len(dataset) - 2)]
        return np.array(data_x), dataset[2:]

    trainX, trainY = create_dataset(dataset)

    model = Sequential()
    model.add(Dense(5, input_dim=1, activation='relu'))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    print("HERE\n\n\n")
    model.fit(trainX, trainY, epochs=200, batch_size=2, verbose=0)

    return model.predict(np.array([dataset[len(dataset) - 1]]))


def home(request):
    return render(request, 'app/home.html')


def dashboard(request):
    update_item = []
    data = Company.objects.filter(user=request.user)
    for item in data:
        ticker = item.company_intial
        predicted_price = predictor(ticker.upper())
        if predicted_price[0][0] < item.stoploss:
            print(str(item.stoploss) + ':' + str(predicted_price[0][0]))
            update_item.append(item.company_intial)

    if update_item:
        for i in update_item:
            temp = Company.objects.get(company_intial=i)
            temp.to_sell = "Yes"
            temp.save()

    data = Company.objects.filter(user=request.user)
    return render(request, 'app/dashboard.html', {'data': data})


def register(request):
    if request.method == 'POST':
        user_form = Sign(request.POST)
        if user_form.is_valid():
            user = user_form.save(commit=False)
            username = user_form.cleaned_data['username']
            password = user_form.cleaned_data['password']
            email = user_form.cleaned_data['email']
            print(email)
            user.set_password(password)
            user.save()
            login(request, authenticate(username=username, password=password,
                                        email=email))
            return redirect('/app/home')
    else:
        user_form = Sign()

    return render(request, 'app/register.html', {'user_form': user_form})


def login_user(request):
    username = password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('/app/home')
    return render(request, 'app/login.html')


def logout_user(request):
    logout(request)


def company(request):
    if request.method == 'POST':
        user = request.user
        ticker = request.POST['ticker']
        name = request.POST['compname']
        amount_of_stock = request.POST['amt']
        pur_price = request.POST['ppps']
        stploss = request.POST['stopl']

        company = Company()
        company.user = user
        company.company_name = name
        company.company_intial = ticker
        company.amount_of_stock = amount_of_stock
        company.purchase_price = pur_price
        company.stoploss = stploss
        company.save()

        # sentiment = get_sentiment(name)
        # predicted_price = predictor(ticker.upper())
        # print(sentiment, predicted_price)
        return redirect('/app/dashboard')
    return render(request, 'app/test.html')