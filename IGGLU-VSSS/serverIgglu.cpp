#include "serverIgglu.h"
#include <QtWebSockets/QWebSocketServer>
#include <QtWebSockets/QtWebSockets>
#include <QtCore>
#include <cstdio>
using namespace std;

QT_USE_NAMESPACE

static QString getIdentifier(QWebSocket *peer)
{
    return QStringLiteral("%1:%2").arg(peer->peerAddress().toString(),
                                       QString::number(peer->peerPort()));
}

serverIgglu::serverIgglu(quint16 port, QObject *parent)
    : QObject{parent},
    m_pWebSocketServer(new QWebSocketServer(QStringLiteral("Igglu Server"),
                                            QWebSocketServer::NonSecureMode,
                                              this))
{
    if (m_pWebSocketServer->listen(QHostAddress::Any, port))
    {
        QTextStream(stdout) << "Chat Server listening on port " << port << '\n';
        connect(m_pWebSocketServer, &QWebSocketServer::newConnection,
                this, &serverIgglu::onNewConnection);
    }
}

void serverIgglu::onNewConnection()
{
    auto pSocket = m_pWebSocketServer->nextPendingConnection();
    QTextStream(stdout) << getIdentifier(pSocket) << " connected!\n";
    pSocket->setParent(this);

    connect(pSocket, &QWebSocket::textMessageReceived,
            this, &serverIgglu::processMessage);
    connect(pSocket, &QWebSocket::disconnected,
            this, &serverIgglu::socketDisconnected);

    m_clients << pSocket;
}

serverIgglu::~serverIgglu()
{
    m_pWebSocketServer->close();
}

void serverIgglu::processMessage(const QString &message)
{
    QTextStream(stdout) << message;
    QWebSocket *pSender = qobject_cast<QWebSocket *>(sender());
    pSender->sendTextMessage("Oi!");
    for (QWebSocket *pClient : std::as_const(m_clients)) {
        if (pClient != pSender) //don't echo message back to sender
            pClient->sendTextMessage(message);
    }
}

void serverIgglu::socketDisconnected()
{
    QWebSocket *pClient = qobject_cast<QWebSocket *>(sender());
    QTextStream(stdout) << getIdentifier(pClient) << " disconnected!\n";
    if (pClient)
    {
        m_clients.removeAll(pClient);
        pClient->deleteLater();
    }
}

