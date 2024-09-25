#include "serverIgglu.h"
#include <QtWebSockets/QWebSocketServer>
#include <QtWebSockets/QtWebSockets>
#include <QtCore>
#include <cstdio>
#include <QDataStream>
#include <QByteArray>
using namespace std;

QT_USE_NAMESPACE

ServerIgglu::ServerIgglu(QObject *parent)
    : QObject{parent}
{}

ServerIgglu::~ServerIgglu() {}

void ServerIgglu::connectWebSocket(quint16 port) {
    QUrl url{"ws://localhost:5001"};

    if(m_webSocket.state() == QAbstractSocket::ConnectedState){
        return;
    }

    m_webSocket.open(url);

    QTextStream(stdout) << "Connected to "<< url.toString()  <<"\n";


    connect(&m_webSocket, &QWebSocket::connected, this, &ServerIgglu::onConnected);
    connect(&m_webSocket, &QWebSocket::disconnected, this, &ServerIgglu::closeWebSocket);
}

void ServerIgglu::closeWebSocket() {
    m_webSocket.close();
    m_webSocket.disconnect();
    qDebug() << "CLOSED EWE SOCKET";
}

void ServerIgglu::onConnected() {

    connect(&m_webSocket, &QWebSocket::textMessageReceived,
            this, &ServerIgglu::processMessage);
}

void ServerIgglu::closed() {
// TODO is this needed?
    qDebug() << "closed";
}

void ServerIgglu::processMessage(const QString &message)
{
    QTextStream(stdout) << "Received float:" << message;
}
void ServerIgglu::sendMessage() {
    m_webSocket.sendTextMessage("message");
}
